from fastapi import FastAPI
from fastapi.responses import JSONResponse
import subprocess
from prometheus_api_client import PrometheusConnect

app = FastAPI()

@app.post("/createDeployment/{deployment_name}")
async def create_deployment(deployment_name: str):
    deployment_yaml = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {deployment_name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {deployment_name}
  template:
    metadata:
      labels:
        app: {deployment_name}
    spec:
      containers:
      - name: {deployment_name}
        image: nginx:latest
        ports:
        - containerPort: 80
    """
    
    with open(f"{deployment_name}.yaml", "w") as f:
        f.write(deployment_yaml)

    try:
        subprocess.run(["kubectl", "apply", "-f", f"{deployment_name}.yaml"], check=True)
        return JSONResponse(status_code=200, content={"message": f"Deployment {deployment_name} created successfully"})
    except subprocess.CalledProcessError as e:
        return JSONResponse(status_code=500, content={"message": f"Error creating deployment {deployment_name}", "details": str(e)})

@app.get("/getPromdetails")
async def get_prom_details():
    prom = PrometheusConnect(url="http://prometheus-server.monitoring.svc.cluster.local:80", disable_ssl=True)
    query = 'up{job="kubernetes-pods"}'
    result = prom.custom_query(query=query)
    return JSONResponse(status_code=200, content={"data": result})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
