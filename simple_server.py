"""
간단한 vLLM 스트리밍 서버 - 핵심 로직만
"""
import argparse
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams

class ChatRequest(BaseModel):
    message: str
    stream: bool = False

app = FastAPI()
llm: AsyncLLMEngine | None = None

@app.on_event("startup")
async def startup():
    global llm, model_name
    llm = AsyncLLMEngine.from_engine_args(AsyncEngineArgs(model=model_name))

@app.post("/chat")
async def chat(request: ChatRequest):
    # 1. 대화 형식으로 프롬프트 만들기
    prompt = f"Human: {request.message}\nBot:"
    
    # 2. 생성 파라미터
    params = SamplingParams(temperature=0.7, max_tokens=100)
    
    # 3. 공통 생성 로직
    if request.stream:
        return StreamingResponse(generate_with_streaming(prompt, params), media_type="text/plain")
    else:
        return await generate_with_normal(prompt, params)

async def generate_with_streaming(prompt: str, params: SamplingParams):
    """스트리밍: 토큰별로 델타만 전송"""
    previous_text = ""
    
    async for output in generate_tokens(prompt, params):
        current_text = output.outputs[0].text
        delta = current_text[len(previous_text):]  # 새로운 부분만
        
        if delta:
            yield f"data: {delta}\n\n"
        previous_text = current_text
    
    yield "data: [DONE]\n\n"

async def generate_with_normal(prompt: str, params: SamplingParams):
    """일반: 완성된 응답만 반환"""
    final_result = None
    
    async for output in generate_tokens(prompt, params):
        final_result = output  # 마지막 결과만 저장
    
    return {"response": final_result.outputs[0].text.strip()}

async def generate_tokens(prompt: str, params: SamplingParams):
    """공통 모델 생성 로직 - 토큰별로 누적 결과 반환"""
    async for output in llm.generate(prompt, params, f"req_{id(prompt)}"):
        yield output

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    global model_name
    model_name = args.model
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port)