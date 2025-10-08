import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .agents.distributed_agent import DistributedAgentNetwork
from .monitoring.dashboard import DashboardManager
from .consensus.voting_system import ConsensusManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global network instance
network_manager = None
dashboard_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global network_manager, dashboard_manager
    logger.info("🚀 Starting Distributed Agent Network...")
    
    # Initialize network with 3 agents
    network_manager = DistributedAgentNetwork()
    await network_manager.initialize_network(num_agents=3)
    
    # Initialize dashboard
    dashboard_manager = DashboardManager(network_manager)
    await dashboard_manager.start()
    
    logger.info("✅ Network initialized successfully")
    yield
    
    # Cleanup
    await network_manager.shutdown()
    logger.info("🛑 Network shutdown complete")

app = FastAPI(title="Distributed Agent Networks", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Distributed Agent Networks - Day 19", "status": "active"}

@app.get("/api/network/status")
async def get_network_status():
    if network_manager:
        return await network_manager.get_network_status()
    return {"error": "Network not initialized"}

@app.post("/api/network/solve")
async def solve_problem(problem_data: dict):
    if network_manager:
        result = await network_manager.solve_collaboratively(problem_data)
        return result
    return {"error": "Network not initialized"}

@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send real-time updates
            status = await network_manager.get_network_status()
            await websocket.send_json(status)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
