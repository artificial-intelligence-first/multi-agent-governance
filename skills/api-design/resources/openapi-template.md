# OpenAPI Template (API Design Skill)

Replace bracketed sections before publication.

```yaml
openapi: 3.1.0
info:
  title: "<Service Name> API"
  version: "v1"
  description: |
    High-level goal of the service and primary consumers.
servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://staging-api.example.com/v1
    description: Staging

paths:
  /projects:
    get:
      summary: List projects visible to the caller.
      tags: [projects]
      operationId: listProjects
      parameters:
        - in: query
          name: page_size
          schema:
            type: integer
            minimum: 1
            maximum: 200
            default: 50
        - in: query
          name: page_token
          schema:
            type: string
          description: Cursor from the previous response.
      responses:
        "200":
          description: Successful response.
          content:
            application/json:
              schema:
                type: object
                required: [projects, next_page_token]
                properties:
                  projects:
                    type: array
                    items:
                      $ref: "#/components/schemas/Project"
                  next_page_token:
                    type: string
                    nullable: true
        "401":
          $ref: "#/components/responses/UnauthorizedError"
        "429":
          $ref: "#/components/responses/RateLimitError"

components:
  schemas:
    Project:
      type: object
      required: [project_id, name, created_at]
      properties:
        project_id:
          type: string
        name:
          type: string
        created_at:
          type: string
          format: date-time
  responses:
    UnauthorizedError:
      description: Authentication failure.
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
    RateLimitError:
      description: Rate limit exceeded.
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
  schemas:
    Error:
      type: object
      required: [code, message, request_id]
      properties:
        code:
          type: string
        message:
          type: string
        request_id:
          type: string
```
