"""Tests for Traefik configuration."""

import pytest
import yaml
from pathlib import Path


@pytest.fixture
def traefik_config_path():
    """Get path to traefik.yml."""
    return Path(__file__).parent.parent / "dockers/traefik/config/traefik.yml"


@pytest.fixture
def traefik_routes_path():
    """Get path to config.yml."""
    return Path(__file__).parent.parent / "dockers/traefik/config/config.yml"


@pytest.fixture
def traefik_config(traefik_config_path):
    """Load and parse traefik.yml."""
    with open(traefik_config_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def traefik_routes(traefik_routes_path):
    """Load and parse config.yml."""
    with open(traefik_routes_path) as f:
        return yaml.safe_load(f)


class TestTraefikGlobalConfig:
    """Test Traefik global configuration."""
    
    def test_traefik_yml_loads(self, traefik_config):
        """Test traefik.yml is valid YAML."""
        assert traefik_config is not None
        assert isinstance(traefik_config, dict)
    
    def test_global_section_exists(self, traefik_config):
        """Test global section is configured."""
        assert "global" in traefik_config
        assert traefik_config["global"]["sendAnonymousUsage"] is True
    
    def test_api_dashboard_enabled(self, traefik_config):
        """Test API dashboard is enabled."""
        assert "api" in traefik_config
        assert traefik_config["api"]["dashboard"] is True
        assert traefik_config["api"]["insecure"] is True
    
    def test_docker_provider_configured(self, traefik_config):
        """Test Docker provider is configured."""
        providers = traefik_config["providers"]
        assert "docker" in providers
        assert providers["docker"]["watch"] is True
        assert providers["docker"]["exposedByDefault"] is False
    
    def test_file_provider_configured(self, traefik_config):
        """Test file provider is configured."""
        providers = traefik_config["providers"]
        assert "file" in providers
        assert providers["file"]["filename"] == "/etc/traefik/config.yml"
        assert providers["file"]["watch"] is True


class TestTraefikEntryPoints:
    """Test Traefik entry points."""
    
    def test_http_entry_point(self, traefik_config):
        """Test HTTP entry point is configured."""
        entry_points = traefik_config["entryPoints"]
        assert "http" in entry_points
        assert entry_points["http"]["address"] == ":80"
    
    def test_https_entry_point(self, traefik_config):
        """Test HTTPS entry point is configured."""
        entry_points = traefik_config["entryPoints"]
        assert "https" in entry_points
        assert entry_points["https"]["address"] == ":443"
    
    def test_postgresql_entry_point(self, traefik_config):
        """Test PostgreSQL TCP entry point is configured."""
        entry_points = traefik_config["entryPoints"]
        assert "postgresql" in entry_points
        assert entry_points["postgresql"]["address"] == ":5432"


class TestTraefikMiddleware:
    """Test Traefik middleware configuration."""
    
    def test_redirect_https_middleware(self, traefik_routes):
        """Test HTTPS redirect middleware."""
        middlewares = traefik_routes["http"]["middlewares"]
        assert "redirect-https" in middlewares
        
        redirect = middlewares["redirect-https"]
        assert redirect["redirectScheme"]["scheme"] == "https"
        assert redirect["redirectScheme"]["permanent"] is True
    
    def test_circuit_breaker_middleware(self, traefik_routes):
        """Test circuit breaker middleware is configured."""
        middlewares = traefik_routes["http"]["middlewares"]
        assert "circuit-breaker" in middlewares
        
        cb = middlewares["circuit-breaker"]["circuitBreaker"]
        assert "NetworkErrorRatio() > 0.5" in cb["expression"]
        assert "ResponseCodeRatio(500, 502, 503) > 0.3" in cb["expression"]
        assert cb["check_period"] == "2s"
        assert cb["fallback_duration"] == "30s"
    
    def test_rate_limit_middleware(self, traefik_routes):
        """Test rate limiting middleware."""
        middlewares = traefik_routes["http"]["middlewares"]
        assert "rate-limit" in middlewares
        
        rate_limit = middlewares["rate-limit"]["rateLimit"]
        assert rate_limit["average"] == 100
        assert rate_limit["period"] == "1s"
        assert rate_limit["burst"] == 50
    
    def test_request_tracing_middleware(self, traefik_routes):
        """Test request tracing middleware adds headers."""
        middlewares = traefik_routes["http"]["middlewares"]
        assert "request-tracing" in middlewares
        
        headers = middlewares["request-tracing"]["headers"]["customRequestHeaders"]
        assert headers["X-Service"] == "NotebookUM-API"
        assert headers["X-Environment"] == "production"
    
    def test_compression_middleware(self, traefik_routes):
        """Test compression middleware."""
        middlewares = traefik_routes["http"]["middlewares"]
        assert "compression" in middlewares
        assert middlewares["compression"]["compress"]["minResponseBodyBytes"] == 1024


class TestTraefikHTTPRouters:
    """Test HTTP routers configuration."""
    
    def test_notebookum_http_router(self, traefik_routes):
        """Test NotebookUM HTTP router exists."""
        routers = traefik_routes["http"]["routers"]
        assert "notebookum-http" in routers
        
        router = routers["notebookum-http"]
        assert "notebookum.universidad.localhost" in router["rule"]
        assert router["service"] == "notebookum"
        assert "redirect-https" in router["middlewares"]
    
    def test_notebookum_https_router_has_security_middleware(self, traefik_routes):
        """Test NotebookUM HTTPS router has rate limit and circuit breaker."""
        routers = traefik_routes["http"]["routers"]
        assert "notebookum-https" in routers
        
        router = routers["notebookum-https"]
        middlewares = router["middlewares"]
        
        assert "rate-limit" in middlewares
        assert "circuit-breaker" in middlewares
        assert "request-tracing" in middlewares
        assert "compression" in middlewares
    
    def test_notebookum_https_router_timeouts(self, traefik_routes):
        """Test NotebookUM HTTPS router has timeouts configured."""
        routers = traefik_routes["http"]["routers"]
        router = routers["notebookum-https"]
        
        assert router["timeoutConnect"] == "10s"
        assert router["timeoutRequest"] == "30s"
        assert router["timeoutIdle"] == "60s"
    
    def test_notebookum_https_router_tls(self, traefik_routes):
        """Test NotebookUM HTTPS router has TLS domains."""
        routers = traefik_routes["http"]["routers"]
        router = routers["notebookum-https"]
        
        assert "tls" in router
        assert len(router["tls"]["domains"]) == 2


class TestTraefikServices:
    """Test HTTP services configuration."""
    
    def test_notebookum_service_exists(self, traefik_routes):
        """Test NotebookUM HTTP service."""
        services = traefik_routes["http"]["services"]
        assert "notebookum" in services
        
        service = services["notebookum"]
        assert service["loadBalancer"]["servers"][0]["url"] == "http://notebookum:8000"
    
    def test_notebookum_service_health_check(self, traefik_routes):
        """Test NotebookUM service has health check."""
        services = traefik_routes["http"]["services"]
        health_check = services["notebookum"]["loadBalancer"]["healthCheck"]
        
        assert health_check["path"] == "/health"
        assert health_check["interval"] == "30s"
        assert health_check["timeout"] == "5s"


class TestTraefikTCPRouters:
    """Test TCP routing for PostgreSQL."""
    
    def test_tcp_section_exists(self, traefik_routes):
        """Test TCP section is configured."""
        assert "tcp" in traefik_routes
    
    def test_postgresql_tcp_router(self, traefik_routes):
        """Test PostgreSQL TCP router."""
        tcp_routers = traefik_routes["tcp"]["routers"]
        assert "postgresql" in tcp_routers
        
        router = tcp_routers["postgresql"]
        assert router["entryPoints"] == ["postgresql"]
        assert router["service"] == "postgresql"
    
    def test_postgresql_tcp_service(self, traefik_routes):
        """Test PostgreSQL TCP service."""
        tcp_services = traefik_routes["tcp"]["services"]
        assert "postgresql" in tcp_services
        
        service = tcp_services["postgresql"]
        assert service["loadBalancer"]["servers"][0]["address"] == "postgres:5432"


class TestTraefikTLS:
    """Test TLS configuration."""
    
    def test_tls_stores_configured(self, traefik_routes):
        """Test TLS stores are configured."""
        tls = traefik_routes["tls"]
        assert "stores" in tls
        assert "default" in tls["stores"]
    
    def test_default_certificate(self, traefik_routes):
        """Test default certificate is set."""
        tls = traefik_routes["tls"]
        cert = tls["stores"]["default"]["defaultCertificate"]
        
        assert cert["certFile"] == "/etc/certs/cert.pem"
        assert cert["keyFile"] == "/etc/certs/key.pem"
    
    def test_certificates_list(self, traefik_routes):
        """Test certificates list."""
        tls = traefik_routes["tls"]
        assert "certificates" in tls
        assert len(tls["certificates"]) > 0
        
        cert = tls["certificates"][0]
        assert cert["certFile"] == "/etc/certs/cert.pem"
        assert cert["keyFile"] == "/etc/certs/key.pem"


class TestTraefikIntegration:
    """Integration tests for Traefik configuration."""
    
    def test_all_routers_have_valid_services(self, traefik_routes):
        """Test all HTTP routers reference valid services."""
        routers = traefik_routes["http"]["routers"]
        services = traefik_routes["http"]["services"]
        
        for router_name, router in routers.items():
            if "service" in router and router["service"] not in ["noop@internal", "api@internal"]:
                assert router["service"] in services, f"Router {router_name} references unknown service {router['service']}"
    
    def test_all_middlewares_referenced_exist(self, traefik_routes):
        """Test all referenced middlewares are defined."""
        http_routes = traefik_routes["http"]
        middlewares = http_routes["middlewares"]
        
        for router_name, router in http_routes["routers"].items():
            if "middlewares" in router:
                for middleware in router["middlewares"]:
                    assert middleware in middlewares, f"Router {router_name} references undefined middleware {middleware}"
    
    def test_circuit_breaker_and_rate_limit_on_notebookum(self, traefik_routes):
        """Test NotebookUM has both circuit breaker and rate limiting."""
        routers = traefik_routes["http"]["routers"]
        
        # Check HTTPS router
        https_router = routers["notebookum-https"]
        assert "circuit-breaker" in https_router["middlewares"]
        assert "rate-limit" in https_router["middlewares"]
        
        # Check generic router
        generic_router = routers["notebookum"]
        assert "circuit-breaker" in generic_router["middlewares"]
        assert "rate-limit" in generic_router["middlewares"]
    
    def test_postgresql_tcp_properly_configured(self, traefik_routes):
        """Test PostgreSQL TCP routing is complete."""
        tcp = traefik_routes["tcp"]
        
        # Check router exists and references service
        assert "postgresql" in tcp["routers"]
        assert tcp["routers"]["postgresql"]["service"] == "postgresql"
        
        # Check service exists and has address
        assert "postgresql" in tcp["services"]
        assert "postgres:5432" in tcp["services"]["postgresql"]["loadBalancer"]["servers"][0]["address"]


class TestDockerComposeConfig:
    """Test docker-compose.yml configuration."""
    
    def test_docker_compose_loads(self):
        """Test docker-compose.yml is valid."""
        compose_path = Path(__file__).parent.parent / "dockers/traefik/docker-compose.yml"
        
        with open(compose_path) as f:
            compose = yaml.safe_load(f)
        
        assert compose is not None
        assert "services" in compose
    
    def test_traefik_ports_exposed(self):
        """Test Traefik exposes required ports."""
        compose_path = Path(__file__).parent.parent / "dockers/traefik/docker-compose.yml"
        
        with open(compose_path) as f:
            compose = yaml.safe_load(f)
        
        reverse_proxy = compose["services"]["reverse-proxy"]
        ports = reverse_proxy["ports"]
        
        # Check required ports
        port_mappings = [str(p) for p in ports]
        assert any("80" in p for p in port_mappings)  # HTTP
        assert any("443" in p for p in port_mappings)  # HTTPS
        assert any("5432" in p for p in port_mappings)  # PostgreSQL
        assert any("8080" in p for p in port_mappings)  # Dashboard
