@echo off
setlocal

if "%~1"=="" (
    echo Usage: deploy-release.cmd ^<release-tag^>
    echo Example: deploy-release.cmd 2b4d303
    exit /b 1
)

set "TAG=%~1"

echo.
echo ==========================================
echo ShopSphere Release Deployment
echo Release Tag: %TAG%
echo ==========================================
echo.

echo [1/6] Verifying backend image...
docker pull sameer340314/shopsphere-backend:%TAG%
if errorlevel 1 exit /b 1

echo.
echo [2/6] Verifying frontend image...
docker pull sameer340314/shopsphere-frontend:%TAG%
if errorlevel 1 exit /b 1

echo.
echo [3/6] Updating Kubernetes backend image...
kubectl set image deployment/shopsphere-backend ^
    shopsphere-backend=sameer340314/shopsphere-backend:%TAG% ^
    -n shopsphere
if errorlevel 1 exit /b 1

echo.
echo [4/6] Updating Kubernetes frontend image...
kubectl set image deployment/shopsphere-frontend ^
    shopsphere-frontend=sameer340314/shopsphere-frontend:%TAG% ^
    -n shopsphere
if errorlevel 1 exit /b 1

echo.
echo [5/6] Waiting for backend rollout...
kubectl rollout status deployment/shopsphere-backend -n shopsphere
if errorlevel 1 exit /b 1

echo.
echo [6/6] Waiting for frontend rollout...
kubectl rollout status deployment/shopsphere-frontend -n shopsphere
if errorlevel 1 exit /b 1

echo.
echo ==========================================
echo ShopSphere release deployed successfully.
echo Release Tag: %TAG%
echo ==========================================
echo.

kubectl get deployments -n shopsphere

endlocal