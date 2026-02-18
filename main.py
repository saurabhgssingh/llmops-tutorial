import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from groq import Groq

app = FastAPI(title="Groq Text Generator", version="0.1.0")


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="User prompt to complete")
    model: str | None = Field(
        default=None,
        description="Optional model override (defaults to GROQ_MODEL or a built-in default)",
    )
    max_tokens: int | None = Field(
        default=512, ge=1, le=4096, description="Max tokens to generate"
    )
    temperature: float | None = Field(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature"
    )


class GenerateResponse(BaseModel):
    text: str
    model: str
    usage: dict | None = None


def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not set in the environment.",
        )
    return Groq(api_key=api_key)


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    client = _get_client()
    model = req.model or os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": req.prompt}],
            max_tokens=req.max_tokens,
            temperature=req.temperature,
        )
    except Exception as exc:
        raise exc
        raise HTTPException(status_code=502, detail=f"Groq API error: {exc}") from exc

    choice = response.choices[0]
    text = choice.message.content or ""
    usage = None
    if getattr(response, "usage", None) is not None:
        usage = (
            response.usage.model_dump()
            if hasattr(response.usage, "model_dump")
            else dict(response.usage)
        )

    return GenerateResponse(text=text, model=model, usage=usage)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
