# OpenAPI Specifications

This directory contains OpenAPI specifications for all Lumina services, providing machine-readable API documentation that can be used for:

- **Code Generation**: Automatic client SDK generation
- **Documentation**: Interactive API documentation
- **Testing**: Automated API testing
- **Validation**: Request/response validation

## 📋 Available Specifications

### [brain-api.yaml](./brain-api.yaml)
**Service**: Brain API (Python FastAPI)  
**Version**: 1.0.0  
**Endpoints**: `/health`, `/ingest`, `/search`

### Features
- Complete request/response schemas
- Comprehensive examples
- Error handling documentation
- Security scheme definitions
- Tag-based endpoint organization

## 🚀 Usage

### Interactive Documentation
Access the interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Code Generation

#### TypeScript Client
```bash
# Install OpenAPI generator
npm install @openapitools/openapi-generator-cli -g

# Generate TypeScript client
openapi-generator-cli generate \
  -i brain-api.yaml \
  -g typescript-axios \
  -o ./generated-client \
  --additional-properties=npmName=lumina-client
```

#### Python Client
```bash
# Generate Python client
openapi-generator-cli generate \
  -i brain-api.yaml \
  -g python \
  -o ./python-client \
  --additional-properties=packageName=lumina_client
```

#### Go Client
```bash
# Generate Go client
openapi-generator-cli generate \
  -i brain-api.yaml \
  -g go \
  -o ./go-client \
  --additional-properties=packageName=lumina
```

### API Testing

#### Postman Collection
```bash
# Convert OpenAPI to Postman collection
openapi-generator-cli generate \
  -i brain-api.yaml \
  -g postman_collection \
  -o ./postman
```

#### Insomnia Collection
```bash
# Generate Insomnia collection
openapi-generator-cli generate \
  -i brain-api.yaml \
  -g insomnia \
  -o ./insomnia
```

### Validation

#### Request Validation (Node.js)
```javascript
const Ajv = require('ajv');
const fs = require('fs');

// Load OpenAPI spec
const openapi = JSON.parse(fs.readFileSync('brain-api.yaml', 'utf8'));

// Create validator
const ajv = new Ajv({ allErrors: true });
const validateDocument = ajv.compile(openapi.components.schemas.Document);

// Validate request
const isValid = validateDocument(requestBody);
if (!isValid) {
  console.error('Validation errors:', validateDocument.errors);
}
```

#### Response Validation (Python)
```python
import yaml
import jsonschema
from jsonschema import validate

# Load OpenAPI spec
with open('brain-api.yaml', 'r') as f:
    openapi_spec = yaml.safe_load(f)

# Validate response
document_schema = openapi_spec['components']['schemas']['Document']
try:
    validate(instance=response_data, schema=document_schema)
except jsonschema.ValidationError as e:
    print(f"Validation error: {e.message}")
```

## 🔧 Development Tools

### Linting and Validation

#### Spectral Linter
```bash
# Install Spectral
npm install -g @stoplight/spectral

# Lint OpenAPI spec
spectral lint brain-api.yaml
```

#### Redoc CLI
```bash
# Install Redoc CLI
npm install -g redoc-cli

# Generate static HTML documentation
redoc-cli bundle brain-api.yaml -o brain-api-docs.html
```

#### Swagger Codegen
```bash
# Generate HTML documentation
swagger-codegen generate \
  -i brain-api.yaml \
  -l html \
  -o ./docs-html
```

### Mock Server

#### Prism Mock Server
```bash
# Install Prism
npm install -g @stoplight/prism-cli

# Start mock server
prism mock brain-api.yaml --port 4010
```

#### Mockoon
1. Import `brain-api.yaml` into Mockoon
2. Start mock server on port 3000
3. Test API endpoints without backend

## 📊 Specification Metrics

### brain-api.yaml Statistics
- **Endpoints**: 3
- **Schemas**: 6
- **Examples**: 10
- **Tags**: 3
- **Security Schemes**: 1

### Coverage Analysis
```bash
# Analyze API coverage
openapi-generator-cli analyze \
  -i brain-api.yaml \
  -o ./analysis
```

## 🔄 Versioning

### Semantic Versioning
OpenAPI specifications follow semantic versioning:
- **Major**: Breaking changes
- **Minor**: New features (non-breaking)
- **Patch**: Bug fixes and documentation

### Version Management
```yaml
# Version in specification
info:
  version: 1.0.0
  
# Version in filename
brain-api-v1.0.0.yaml
```

### Breaking Changes
Breaking changes require:
1. Increment major version
2. Update all clients
3. Migration guide
4. Deprecation period

## 📝 Customization

### Extension Points
```yaml
# Custom extensions
x-custom-extension: value
x-provider: lumina
x-maturity: production
```

### Server Configuration
```yaml
servers:
  - url: http://localhost:8000
    description: Development
  - url: https://api.lumina.example.com
    description: Production
  - url: https://staging-api.lumina.example.com
    description: Staging
```

### Tag Organization
```yaml
tags:
  - name: Health
    description: Service monitoring
    x-display-name: "Health Checks"
  - name: Documents
    description: Document management
    x-display-name: "Documents"
  - name: Search
    description: Search functionality
    x-display-name: "Search"
```

## 🔒 Security

### Authentication Schemes
```yaml
securitySchemes:
  ApiKeyAuth:
    type: apiKey
    in: header
    name: X-API-Key
    description: API key for authentication
  
  BearerAuth:
    type: http
    scheme: bearer
    bearerFormat: JWT
    description: JWT token for authentication
```

### Security Requirements
```yaml
security:
  - ApiKeyAuth: []
  - BearerAuth: []
```

### OAuth2 Configuration
```yaml
securitySchemes:
  OAuth2:
    type: oauth2
    flows:
      authorizationCode:
        authorizationUrl: https://auth.lumina.example.com/oauth/authorize
        tokenUrl: https://auth.lumina.example.com/oauth/token
        scopes:
          read: Read access
          write: Write access
          admin: Admin access
```

## 📈 Monitoring and Analytics

### API Usage Tracking
```yaml
# Custom extensions for monitoring
x-monitoring:
  metrics:
    - request_count
    - response_time
    - error_rate
  alerts:
    - high_error_rate
    - slow_response_time
```

### Rate Limiting
```yaml
x-rate-limiting:
  requests_per_minute: 100
  burst_size: 20
  strategy: sliding_window
```

### Caching
```yaml
x-cache:
  ttl: 300
  strategy: memory
  vary_by: [query, headers]
```

## 🧪 Testing

### Contract Testing
```javascript
// Using Dredd for contract testing
const Dredd = require('dredd');

const dredd = new Dredd({
  spec: 'brain-api.yaml',
  server: 'http://localhost:8000',
});

dredd.run((err, stats) => {
  if (err) console.error(err);
  console.log('Test results:', stats);
});
```

### Integration Testing
```python
# Using pytest-openapi for Python testing
import pytest
from openapi_core import Spec, validate_request

@pytest.fixture
def spec():
    return Spec.from_file('brain-api.yaml')

def test_search_endpoint(spec):
    request = MockRequest('GET', '/search?query=test')
    result = validate_request(spec, request)
    assert result.is_valid
```

## 📚 Resources

### Documentation Tools
- **Swagger UI**: Interactive API documentation
- **Redoc**: Clean API documentation
- **Spectacle**: Static documentation generator

### Code Generation Tools
- **OpenAPI Generator**: Multi-language client generation
- **Swagger Codegen**: Alternative code generator
- **NSwag**: .NET client generation

### Testing Tools
- **Dredd**: Contract testing
- **Postman**: API testing and documentation
- **Insomnia**: API client and testing

### Validation Tools
- **Spectral**: Linting and validation
- **Ajv**: JSON schema validation
- **jsonschema**: Python validation library

---

*For detailed API specifications, see the individual YAML files in this directory.*
