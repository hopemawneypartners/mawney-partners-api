# API Alignment Check: Swift App vs Python API

## Summary
This document compares the API endpoints expected by the Swift iOS app with what's implemented in the Python API (`app.py`).

## ✅ Endpoints Present in Both

### 1. Articles & News
- ✅ `GET /api/articles` - Present in both
- ✅ `GET /api/ai/summary` - Present in both

### 2. AI Assistant
- ✅ `POST /api/ai-assistant` - Present in both
- ✅ `POST /api/ai/chat` - Present in both

### 3. Chat System
- ✅ `GET /api/chat/sessions` - Present in both
- ✅ `POST /api/chat/sessions` - Present in both
- ✅ `DELETE /api/chat/sessions/<chat_id>` - Present in both
- ✅ `GET /api/chat/sessions/<chat_id>/conversations` - Present in both
- ✅ `POST /api/chat/sessions/<chat_id>/conversations` - Present in both
- ✅ `GET /api/chat/current` - Present in both
- ✅ `POST /api/chat/current` - Present in both

### 4. User Profile
- ✅ `GET /api/user/profile` - Present in both
- ✅ `POST /api/user/profile` - Present in both

### 5. Notifications
- ✅ `GET /api/notifications` - Present in both
- ✅ `POST /api/test-notification` - Present in both

### 6. System
- ✅ `GET /api/health` - Present in both
- ✅ `POST /api/trigger-collection` - Present in both
- ✅ `GET /api/download-cv/<filename>` - Present in both

---

## ❌ Missing Endpoints in Python API

The following endpoints are used by the Swift app but are **NOT FOUND** in the Python API:

### 1. User-Specific Data Endpoints

#### ❌ `GET /api/user-todos?email={email}`
- **Used by:** `Models/Todo.swift` (line 215)
- **Purpose:** Fetch todos for a specific user
- **Expected Response:** `{ "success": bool, "todos": [...], "error": string? }`

#### ❌ `POST /api/user-todos`
- **Used by:** `Models/Todo.swift` (line 331)
- **Purpose:** Save todos for a user
- **Expected Payload:** `{ "email": string, "todos": [...] }`
- **Expected Response:** `{ "success": bool, "error": string? }`

#### ❌ `GET /api/user-call-notes?email={email}`
- **Used by:** `Models/CallNote.swift` (line 161)
- **Purpose:** Fetch call notes for a specific user
- **Expected Response:** `{ "success": bool, "call_notes": [...], "error": string? }`

#### ❌ `POST /api/user-call-notes`
- **Used by:** `Models/CallNote.swift` (line 206)
- **Purpose:** Save call notes for a user
- **Expected Payload:** `{ "email": string, "call_notes": [...] }`
- **Expected Response:** `{ "success": bool, "error": string? }`

#### ❌ `GET /api/user-chats?email={email}`
- **Used by:** `Services/ChatAPIService.swift` (line 12)
- **Purpose:** Fetch chats for a specific user
- **Expected Response:** `{ "success": bool, "chats": [...], "error": string? }`

#### ❌ `POST /api/user-chats`
- **Used by:** `Services/ChatAPIService.swift` (line 49)
- **Purpose:** Save chats for a user
- **Expected Payload:** `{ "email": string, "chats": [...] }`
- **Expected Response:** `{ "success": bool, "error": string? }`

#### ❌ `GET /api/user-messages?chat_id={chatId}`
- **Used by:** `Services/ChatAPIService.swift` (line 78)
- **Purpose:** Fetch messages for a specific chat
- **Expected Response:** `{ "success": bool, "messages": [...], "error": string? }`

#### ❌ `POST /api/user-messages`
- **Used by:** `Services/ChatAPIService.swift` (line 100)
- **Purpose:** Save messages for a chat
- **Expected Payload:** `{ "chat_id": string, "messages": [...], "sender_email": string? }`
- **Expected Response:** `{ "success": bool, "error": string? }`

### 2. Industry Moves Endpoints

#### ❌ `GET /api/industry-moves?email={email}`
- **Used by:** `Services/MoveService.swift` (line 39)
- **Purpose:** Fetch industry moves for a user
- **Expected Response:** `{ "success": bool, "moves": [...], "error": string? }`

#### ❌ `POST /api/industry-moves`
- **Used by:** `Services/MoveService.swift` (line 101)
- **Purpose:** Create a new industry move
- **Expected Payload:** `{ "email": string, "move": {...} }`
- **Expected Response:** `{ "success": bool, "move": {...}, "error": string? }`

#### ❌ `DELETE /api/industry-moves/{moveId}?email={email}`
- **Used by:** `Services/MoveService.swift` (line 174)
- **Purpose:** Delete an industry move
- **Expected Response:** `{ "success": bool, "error": string? }`

#### ❌ `PUT /api/industry-moves/{moveId}?email={email}`
- **Used by:** `Services/MoveService.swift` (line 233)
- **Purpose:** Update an industry move
- **Expected Payload:** `{ "move": {...} }`
- **Expected Response:** `{ "success": bool, "move": {...}, "error": string? }`

#### ❌ `GET /api/industry-moves/search/{name}?email={email}`
- **Used by:** `Services/MoveService.swift` (line 267)
- **Purpose:** Search industry moves by name
- **Expected Response:** `{ "success": bool, "moves": [...], "error": string? }`

#### ❌ `GET /api/industry-moves/company/{company}?email={email}`
- **Used by:** `Services/MoveService.swift` (line 295)
- **Purpose:** Get moves for a specific company
- **Expected Response:** `{ "success": bool, "moves": [...], "error": string? }`

#### ❌ `GET /api/industry-moves/leaderboard?email={email}`
- **Used by:** `Services/MoveService.swift` (line 322)
- **Purpose:** Get leaderboard of top movers
- **Expected Response:** `{ "success": bool, "leaderboard": [...], "error": string? }`

#### ❌ `GET /api/industry-moves/stats?email={email}`
- **Used by:** `Services/MoveService.swift` (line 348)
- **Purpose:** Get statistics about moves
- **Expected Response:** `{ "success": bool, "stats": {...}, "error": string? }`

#### ❌ `GET /api/industry-moves/autocomplete?query={query}&email={email}`
- **Used by:** `Services/MoveService.swift` (line 374)
- **Purpose:** Get autocomplete suggestions
- **Expected Response:** `{ "success": bool, "suggestions": [...], "error": string? }`

### 3. Compensation Endpoints

#### ❌ `GET /api/compensations?email={email}`
- **Used by:** `Models/Compensation.swift` (line 428)
- **Purpose:** Fetch compensations for a user
- **Expected Response:** `{ "success": bool, "compensations": [...], "error": string? }`

#### ❌ `POST /api/compensations?email={email}`
- **Used by:** `Models/Compensation.swift` (line 614)
- **Purpose:** Save compensations for a user
- **Expected Payload:** `{ "compensations": [...] }`
- **Expected Response:** `{ "success": bool, "error": string? }`

### 4. Call Notes Endpoints

#### ❌ `POST /api/share-call-note`
- **Used by:** `Views/CallNotesView.swift` (line 740)
- **Purpose:** Share a call note with other users
- **Expected Payload:** `{ "call_note_id": string, "recipient_emails": [...], "sender_email": string }`
- **Expected Response:** `{ "success": bool, "error": string? }`

#### ❌ `POST /api/assign-task`
- **Used by:** `Models/Todo.swift` (line 370)
- **Purpose:** Assign a task to other users
- **Expected Payload:** `{ "task_id": string, "assignee_emails": [...], "assigner_email": string }`
- **Expected Response:** `{ "success": bool, "error": string? }`

### 5. Device Token Registration

#### ❌ `POST /api/register-device-token`
- **Used by:** `AppDelegate.swift` (line 32) and `MP_APP_V4App.swift` (line 133)
- **Purpose:** Register device token for push notifications
- **Expected Payload:** `{ "device_token": string, "email": string, "platform": string }`
- **Expected Response:** `{ "success": bool, "error": string? }`

### 6. Call Notes Summary

#### ❌ `POST /api/call-notes/summary`
- **Used by:** `Services/AISummaryService.swift` (line 12)
- **Purpose:** Generate AI summary from call note transcript
- **Expected Payload:** `{ "transcript": string, "context": {...} }`
- **Expected Response:** `{ "success": bool, "summary": {...}, "error": string? }`

---

## 📊 Summary Statistics

- **Total Endpoints in Python API:** 18
- **Total Endpoints Used by Swift App:** 35+
- **Missing Endpoints:** 20+

## 🔧 Recommendations

1. **Implement Missing User-Specific Data Endpoints:**
   - User todos (GET/POST)
   - User call notes (GET/POST)
   - User chats (GET/POST)
   - User messages (GET/POST)

2. **Implement Industry Moves System:**
   - Full CRUD operations
   - Search and filtering
   - Leaderboard and stats
   - Autocomplete

3. **Implement Compensation System:**
   - GET and POST endpoints
   - User-specific data storage

4. **Implement Sharing & Assignment:**
   - Share call notes
   - Assign tasks

5. **Implement Device Management:**
   - Device token registration for push notifications

6. **Implement Call Notes Summary:**
   - Dedicated endpoint for AI summarization

## 📝 Notes

- The Python API currently has in-memory storage (`user_todos`, `user_call_notes`, `user_chats`, etc.) but no HTTP endpoints to access them
- The chat system endpoints exist but use a different structure (`/api/chat/sessions`) vs what the Swift app expects (`/api/user-chats`)
- Industry moves and compensation systems are completely missing from the API
- The API needs to support email-based user identification for all user-specific endpoints
