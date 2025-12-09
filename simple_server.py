"""
간단한 vLLM 스트리밍 서버 - 텍스트/이미지 생성 지원
"""
import argparse
import asyncio
import base64
from io import BytesIO
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams
import torch

class ChatRequest(BaseModel):
    message: str
    stream: bool = False

class ImageRequest(BaseModel):
    prompt: str
    steps: int = 20

app = FastAPI()
llm: AsyncLLMEngine | None = None
image_pipe = None

@app.on_event("startup")
async def startup():
    global llm, model_name, image_pipe, image_model_name
    llm = AsyncLLMEngine.from_engine_args(AsyncEngineArgs(model=model_name))
    
    if image_model_name:
        from diffusers import StableDiffusionPipeline
        print(f"Loading image generation model: {image_model_name}")
        image_pipe = StableDiffusionPipeline.from_pretrained(
            image_model_name, 
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        if torch.cuda.is_available():
            image_pipe = image_pipe.to("cuda")
        print("Image generation model loaded successfully")
    else:
        print("No image model specified, image generation disabled")

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

@app.post("/image")
async def generate_image(request: ImageRequest):
    """이미지 생성 엔드포인트"""
    if image_pipe is None:
        return {"error": "Image generation model not loaded"}
    
    try:
        # 비동기 처리를 위해 별도 스레드에서 실행
        loop = asyncio.get_event_loop()
        image = await loop.run_in_executor(
            None, 
            lambda: image_pipe(request.prompt, num_inference_steps=request.steps).images[0]
        )
        
        # PIL 이미지를 base64로 변환
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "image": f"data:image/png;base64,{img_str}",
            "prompt": request.prompt,
            "steps": request.steps
        }
    except Exception as e:
        return {"error": f"Image generation failed: {str(e)}"}

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
    parser.add_argument("--model", required=True, help="Text generation model")
    parser.add_argument("--image-model", help="Image generation model (optional)")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    global model_name, image_model_name
    model_name = args.model
    image_model_name = args.image_model
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port)