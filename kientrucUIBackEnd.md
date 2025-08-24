Dựa trên cấu trúc project của bạn, tôi sẽ tạo các diagram Mermaid để minh họa kiến trúc và luồng dữ liệu:

## **1. Architecture Overview**

```mermaid
graph TB
    subgraph "Frontend (Next.js - Port 3000)"
        A[Browser] --> B[Next.js App]
        B --> C[App Layout]
        C --> D[Chat Container]
        C --> E[Document Sidebar]
        
        subgraph "UI Components"
            F[Button]
            G[Card]
            H[Input]
        end
        
        subgraph "API Client"
            I[client.ts]
            J[Chat API]
            K[Documents API]
        end
        
        D --> F
        E --> F
        D --> G
        E --> G
        
        D --> I
        E --> I
        I --> J
        I --> K
    end
    
    subgraph "Backend (FastAPI - Port 8000)"
        L[FastAPI App] --> M[CORS Middleware]
        M --> N[Chat Routes]
        M --> O[Document Routes]
        
        subgraph "Services"
            P[Chat Service]
            Q[Document Service]
        end
        
        subgraph "Models"
            R[Schemas]
            S[Pydantic Models]
        end
        
        subgraph "Storage"
            T[In-Memory Store]
            U[File System]
            V[uploads/]
            W[logs/]
        end
        
        N --> P
        O --> Q
        P --> R
        Q --> R
        P --> T
        Q --> U
        U --> V
        L --> W
    end
    
    subgraph "Docker Environment"
        X[docker-compose.yml]
        Y[rag-ui container]
        Z[rag-backend container]
    end
    
    J -.->|HTTP POST/GET| N
    K -.->|HTTP POST/GET/DELETE| O
    
    X --> Y
    X --> Z
    Y --> B
    Z --> L
    
    classDef frontend fill:#e1f5fe
    classDef backend fill:#f3e5f5
    classDef storage fill:#fff3e0
    classDef docker fill:#e8f5e8
    
    class A,B,C,D,E,F,G,H,I,J,K frontend
    class L,M,N,O,P,Q,R,S backend
    class T,U,V,W storage
    class X,Y,Z docker
```

## **2. Data Flow Diagram**

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend (Next.js)
    participant API as API Client
    participant BE as Backend (FastAPI)
    participant FS as File System
    participant MEM as Memory Store
    
    Note over U,MEM: Chat Flow
    U->>FE: Types message in ChatContainer
    FE->>API: chatAPI.sendMessage(message)
    API->>BE: POST /api/v1/chat
    BE->>MEM: Store user message
    BE->>BE: Generate AI response
    BE->>MEM: Store AI response
    BE-->>API: ChatResponse + sources
    API-->>FE: Response data
    FE->>FE: Update chat UI
    FE-->>U: Display AI response
    
    Note over U,MEM: Document Upload Flow
    U->>FE: Clicks upload in DocumentSidebar
    FE->>FE: Open file picker
    U->>FE: Selects file
    FE->>API: documentsAPI.upload(file)
    API->>BE: POST /api/v1/documents/upload
    BE->>BE: Validate file type & size
    BE->>FS: Save file to uploads/
    BE->>MEM: Store document metadata
    BE-->>API: Upload success response
    API-->>FE: Upload confirmation
    FE->>FE: Refresh document list
    FE-->>U: Show success message
    
    Note over U,MEM: Document List Flow
    FE->>API: documentsAPI.list()
    API->>BE: GET /api/v1/documents
    BE->>MEM: Retrieve document list
    BE-->>API: List of documents
    API-->>FE: Document data
    FE->>FE: Update DocumentSidebar
    FE-->>U: Display document list
```

## **3. Component Architecture**

```mermaid
graph TD
    subgraph "Frontend Component Hierarchy"
        A[layout.tsx] --> B[Providers.tsx]
        B --> C[page.tsx]
        C --> D[AppLayout]
        
        D --> E[Header]
        D --> F[Main Content]
        
        F --> G[DocumentSidebar]
        F --> H[ChatContainer]
        
        G --> I[Upload Button]
        G --> J[Document List]
        G --> K[Storage Info]
        
        H --> L[Message Display]
        H --> M[Chat Input]
        H --> N[Send Button]
        
        subgraph "Shared UI Components"
            O[Button.tsx]
            P[Card.tsx]
            Q[utils.ts]
        end
        
        I --> O
        N --> O
        L --> P
        J --> P
        
        O --> Q
        P --> Q
    end
    
    subgraph "API Layer"
        R[client.ts] --> S[chatAPI]
        R --> T[documentsAPI]
        
        S --> U[sendMessage]
        S --> V[getHistory]
        
        T --> W[upload]
        T --> X[list]
        T --> Y[delete]
    end
    
    H --> S
    G --> T
    
    classDef component fill:#bbdefb
    classDef ui fill:#c8e6c9
    classDef api fill:#ffe0b2
    
    class A,B,C,D,E,F,G,H,I,J,K,L,M,N component
    class O,P,Q ui
    class R,S,T,U,V,W,X,Y api
```

## **4. API Endpoints Mapping**

```mermaid
graph LR
    subgraph "Frontend API Calls"
        A[chatAPI.sendMessage] 
        B[documentsAPI.upload]
        C[documentsAPI.list]
        D[documentsAPI.delete]
    end
    
    subgraph "Backend Endpoints"
        E[POST /api/v1/chat]
        F[POST /api/v1/documents/upload]
        G[GET /api/v1/documents]
        H[DELETE /api/v1/documents/:id]
        I[GET /health]
        J[GET /]
    end
    
    subgraph "Backend Services"
        K[generate_demo_response]
        L[file validation]
        M[file storage]
        N[metadata management]
    end
    
    A --> E
    B --> F
    C --> G
    D --> H
    
    E --> K
    F --> L
    F --> M
    F --> N
    G --> N
    H --> M
    H --> N
    
    classDef frontend fill:#e3f2fd
    classDef backend fill:#fce4ec
    classDef service fill:#f1f8e9
    
    class A,B,C,D frontend
    class E,F,G,H,I,J backend
    class K,L,M,N service
```

## **5. File System & Data Flow**

```mermaid
graph TB
    subgraph "Project Structure"
        A[UI Root]
        
        subgraph "Frontend (src/)"
            B[app/]
            C[components/]
            D[lib/]
            
            B --> E[layout.tsx]
            B --> F[page.tsx]
            B --> G[globals.css]
            
            C --> H[feature/Chat/]
            C --> I[feature/Document/]
            C --> J[ui/]
            C --> K[layout/]
            
            D --> L[api/client.ts]
            D --> M[utils.ts]
        end
        
        subgraph "Backend (backend/)"
            N[main.py]
            O[config.py]
            P[requirements.txt]
            
            Q[models/] --> R[schemas.py]
            S[routes/] --> T[chat.py]
            S --> U[documents.py]
            V[services/] --> W[chat_service.py]
            V --> X[document_service.py]
            Y[utils/] --> Z[__init__.py]
            
            AA[uploads/] --> AB[uploaded files]
            AC[logs/] --> AD[application logs]
        end
        
        subgraph "Docker"
            AE[docker-compose.yml]
            AF[Dockerfile]
            AG[Dockerfile.dev]
        end
        
        A --> B
        A --> N
        A --> AE
    end
    
    subgraph "Runtime Data Flow"
        AH[User Input] --> AI[Frontend Components]
        AI --> AJ[API Client]
        AJ --> AK[HTTP Request]
        AK --> AL[FastAPI Routes]
        AL --> AM[Services]
        AM --> AN[Data Storage]
        AN --> AO[Response]
        AO --> AP[Frontend Update]
        AP --> AQ[UI Render]
    end
    
    classDef frontend fill:#e8f5e8
    classDef backend fill:#fff3e0
    classDef docker fill:#e1f5fe
    classDef flow fill:#fce4ec
    
    class B,C,D,E,F,G,H,I,J,K,L,M frontend
    class N,O,P,Q,R,S,T,U,V,W,X,Y,Z,AA,AB,AC,AD backend
    class AE,AF,AG docker
    class AH,AI,AJ,AK,AL,AM,AN,AO,AP,AQ flow
```

## **6. Docker Container Communication**

```mermaid
graph TD
    subgraph "Docker Network"
        A[Host Machine<br/>localhost]
        
        subgraph "rag-ui Container<br/>Port 3000"
            B[Next.js Dev Server]
            C[Hot Reload]
            D[Volume Mounts:<br/>src/, public/]
        end
        
        subgraph "rag-backend Container<br/>Port 8000"
            E[FastAPI Server]
            F[Uvicorn ASGI]
            G[Volume Mounts:<br/>uploads/, logs/]
        end
        
        H[docker-compose.yml]
    end
    
    subgraph "Network Communication"
        I[Browser :3000] --> J[Frontend Container]
        J --> K[API Calls]
        K --> L[Backend Container :8000]
        L --> M[File System]
        L --> N[Memory Store]
    end
    
    A --> B
    A --> E
    H --> B
    H --> E
    
    B --> C
    B --> D
    E --> F
    E --> G
    
    I -.->|HTTP| B
    J -.->|HTTP| E
    
    classDef host fill:#f0f0f0
    classDef container fill:#e3f2fd
    classDef communication fill:#fff3e0
    
    class A,H host
    class B,C,D,E,F,G container
    class I,J,K,L,M,N communication
```

## **Key Points về Architecture:**

### **Frontend (Next.js)**
- **Port**: 3000
- **Tech Stack**: React 18, TypeScript, Tailwind CSS
- **Structure**: App Router, Component-based, API client layer
- **Features**: Chat UI, Document upload, Responsive design

### **Backend (FastAPI)**  
- **Port**: 8000
- **Tech Stack**: Python 3.11, FastAPI, Pydantic
- **Structure**: Routes, Services, Models, File storage
- **Features**: RESTful APIs, File upload, CORS, Auto docs

### **Communication**
- **Protocol**: HTTP/REST
- **Data Format**: JSON
- **File Upload**: multipart/form-data
- **CORS**: Enabled for localhost:3000

### **Docker Setup**
- **Containers**: 2 (UI + Backend)
- **Networking**: Bridge network
- **Volumes**: Source code, uploads, logs
- **Development**: Hot reload enabled

Kiến trúc này đảm bảo tách biệt concerns, dễ scale, và maintainable!