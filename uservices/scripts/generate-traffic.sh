#!/bin/bash

# Traffic Generation Script for InvestPulse Microservices Observability
# 
# Purpose: Generate HTTP traffic to all microservices to produce telemetry data
# for testing and validating the LGTM stack integration (Loki, Grafana, Tempo, Metrics)
#
# What this script does:
# 1. Checks health of all services via actuator endpoints
# 2. Generates sample traffic to each service's business logic endpoints
# 3. Queries actuator metrics to trigger OTLP metric exports
# 4. Creates distributed traces across service boundaries
# 5. Produces logs at various levels for Loki aggregation
#
# Usage:
#   bash scripts/generate-traffic.sh [iterations] [delay_seconds]
#
# Examples:
#   bash scripts/generate-traffic.sh              # Run 10 iterations with 2s delay (default)
#   bash scripts/generate-traffic.sh 50 5         # Run 50 iterations with 5s delay
#   bash scripts/generate-traffic.sh infinite 1   # Run continuously with 1s delay

set -e  # Exit on error

# Configuration
ITERATIONS="${1:-10}"          # Number of traffic generation cycles (default: 10)
DELAY="${2:-2}"                # Delay between cycles in seconds (default: 2)

# Service endpoints (adjust ports if your configuration differs)
CONFIG_SERVER="http://localhost:9002"
SENTIMENT_ANALYZER="http://localhost:9001"
REDDIT_INGESTOR="http://localhost:9003"

# Color codes for pretty output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a service is healthy
check_health() {
    local service_name=$1
    local service_url=$2
    
    log_info "Checking health of ${service_name}..."
    
    if curl -sf "${service_url}/actuator/health" > /dev/null 2>&1; then
        log_success "${service_name} is healthy"
        return 0
    else
        log_warning "${service_name} is not responding at ${service_url}"
        return 1
    fi
}

# Function to hit actuator endpoints (generates metrics and traces)
hit_actuator_endpoints() {
    local service_name=$1
    local service_url=$2
    
    log_info "Hitting actuator endpoints for ${service_name}..."
    
    # Health endpoint - generates health check traces
    curl -sf "${service_url}/actuator/health" > /dev/null 2>&1 || true
    
    # Info endpoint - generates application info traces
    curl -sf "${service_url}/actuator/info" > /dev/null 2>&1 || true
    
    # Metrics endpoint - triggers OTLP metrics export
    curl -sf "${service_url}/actuator/metrics" > /dev/null 2>&1 || true
    
    log_success "Actuator endpoints hit for ${service_name}"
}

# Function to generate business logic traffic (if endpoints exist)
generate_business_traffic() {
    local iteration=$1
    
    log_info "Generating business traffic (iteration ${iteration})..."
    
    # Config Server: Fetch configuration for sentiment-analyzer
    # This generates distributed traces across config retrieval
    if curl -sf "${CONFIG_SERVER}/sentiment-analyzer/default" > /dev/null 2>&1; then
        log_success "Config Server: Fetched sentiment-analyzer config"
    fi
    
    # Config Server: Fetch configuration for reddit-ingestor
    if curl -sf "${CONFIG_SERVER}/reddit-ingestor/default" > /dev/null 2>&1; then
        log_success "Config Server: Fetched reddit-ingestor config"
    fi
    
    # Note: Sentiment analyzer and Reddit ingestor are primarily Kafka consumers
    # They don't expose REST endpoints for business logic by default
    # Traffic generation focuses on actuator endpoints to produce observability data
    
    log_success "Business traffic generated for iteration ${iteration}"
}

# Main function
main() {
    echo ""
    log_info "=========================================="
    log_info "  InvestPulse Traffic Generator for LGTM"
    log_info "=========================================="
    echo ""
    log_info "Configuration:"
    log_info "  Iterations: ${ITERATIONS}"
    log_info "  Delay: ${DELAY} seconds"
    echo ""
    
    # Pre-flight checks: Verify all services are healthy
    log_info "Running pre-flight health checks..."
    echo ""
    
    all_healthy=true
    check_health "Config Server" "${CONFIG_SERVER}" || all_healthy=false
    check_health "Sentiment Analyzer" "${SENTIMENT_ANALYZER}" || all_healthy=false
    check_health "Reddit Ingestor" "${REDDIT_INGESTOR}" || all_healthy=false
    
    echo ""
    
    if [ "$all_healthy" = false ]; then
        log_warning "Some services are not healthy. Traffic generation will continue, but results may be incomplete."
        log_info "Ensure all services are running: mvnd spring-boot:run -pl <service-name>"
        echo ""
        sleep 2
    else
        log_success "All services are healthy! Starting traffic generation..."
        echo ""
        sleep 1
    fi
    
    # Traffic generation loop
    if [ "$ITERATIONS" = "infinite" ]; then
        log_info "Running in infinite loop mode. Press Ctrl+C to stop."
        echo ""
        iteration=1
        while true; do
            log_info "--- Iteration ${iteration} ---"
            
            hit_actuator_endpoints "Config Server" "${CONFIG_SERVER}"
            hit_actuator_endpoints "Sentiment Analyzer" "${SENTIMENT_ANALYZER}"
            hit_actuator_endpoints "Reddit Ingestor" "${REDDIT_INGESTOR}"
            
            generate_business_traffic "${iteration}"
            
            log_info "Sleeping for ${DELAY} seconds..."
            echo ""
            sleep "${DELAY}"
            
            iteration=$((iteration + 1))
        done
    else
        for ((i=1; i<=ITERATIONS; i++)); do
            log_info "--- Iteration ${i}/${ITERATIONS} ---"
            
            hit_actuator_endpoints "Config Server" "${CONFIG_SERVER}"
            hit_actuator_endpoints "Sentiment Analyzer" "${SENTIMENT_ANALYZER}"
            hit_actuator_endpoints "Reddit Ingestor" "${REDDIT_INGESTOR}"
            
            generate_business_traffic "${i}"
            
            if [ $i -lt $ITERATIONS ]; then
                log_info "Sleeping for ${DELAY} seconds..."
                echo ""
                sleep "${DELAY}"
            fi
        done
    fi
    
    echo ""
    log_success "=========================================="
    log_success "  Traffic generation complete!"
    log_success "=========================================="
    echo ""
    log_info "Next steps:"
    log_info "  1. Open Grafana at http://localhost:3000 (admin/admin)"
    log_info "  2. Navigate to 'Explore' in the left sidebar"
    log_info "  3. Select 'Tempo' datasource to view traces"
    log_info "  4. Select 'Loki' datasource to view logs"
    log_info "  5. Use query: {service_name=\"sentiment-analyzer\"} to filter logs"
    log_info "  6. Click on trace IDs in logs to correlate with traces"
    echo ""
}

# Trap Ctrl+C for graceful shutdown
trap 'echo ""; log_info "Caught interrupt signal. Exiting..."; exit 0' INT

# Execute main function
main
