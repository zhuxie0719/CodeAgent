from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Comprehensive Detection API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Starting API...")
    uvicorn.run(app, host="0.0.0.0", port=5002)
