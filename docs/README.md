# Digital Human Documentation

This directory contains comprehensive documentation for the Digital Human project, including the Pipecat-inspired architecture refactoring.

## 📚 Documentation Index

### Architecture & Refactoring

1. **[REFACTORING_OVERVIEW.md](./REFACTORING_OVERVIEW.md)** - **START HERE**
   - Executive summary of the refactoring project
   - Quick navigation to all other docs
   - Timeline and migration phases

2. **[ARCHITECTURE_PROPOSAL.md](./ARCHITECTURE_PROPOSAL.md)**
   - Complete architectural design
   - Pipecat-style frame-based pipeline architecture
   - Directory structure proposal
   - Benefits and design rationale

3. **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)**
   - Step-by-step migration instructions
   - Phase-by-phase implementation plan
   - Code examples for each phase
   - Testing and rollback strategies

4. **[COMPLETE_PIPELINE_EXAMPLE.md](./COMPLETE_PIPELINE_EXAMPLE.md)**
   - End-to-end working example
   - Conversational avatar pipeline
   - Full implementations
   - Performance characteristics

### Project Documentation

5. **[architecture.md](./architecture.md)**
   - Current system architecture
   - Component descriptions

6. **[development.md](./development.md)**
   - Development guidelines
   - Coding standards

7. **[deployment.md](./deployment.md)**
   - Deployment instructions
   - Environment configuration

8. **[environment-setup.md](./environment-setup.md)**
   - Setup instructions
   - Dependencies

9. **[api-reference.md](./api-reference.md)**
   - API documentation
   - Endpoint references

10. **[branch-rule.md](./branch-rule.md)**
    - Git branching strategy
    - Contribution guidelines

11. **[documents.md](./documents.md)**
    - Documentation overview

---

## 🎯 Quick Links

**For Reviewers**: Read [REFACTORING_OVERVIEW.md](./REFACTORING_OVERVIEW.md)

**For Implementers**: Read [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)

**For Examples**: Read [COMPLETE_PIPELINE_EXAMPLE.md](./COMPLETE_PIPELINE_EXAMPLE.md)

---

## 📝 Key Changes in Refactoring

### Architecture
- **Frame-based pipeline**: All data flows as typed frames (TextFrame, AudioFrame, etc.)
- **Composable processors**: Small, focused components linked together
- **Clean separation**: Core, Processors, Services, Transports

### Naming
- `BaseReal` → `BaseAvatarProcessor` (clearer naming!)
- `services/real.py` → `services/avatar_models/model_manager.py`

### Structure
```
src/
├── core/              # Framework (frames, processors, pipelines)
├── processors/        # Avatar, audio, video, text processors
├── transports/        # WebRTC, VirtualCam, Local
└── services/          # TTS, LLM, ASR, Avatar models
```

---

**Last Updated**: 2025-12-26
