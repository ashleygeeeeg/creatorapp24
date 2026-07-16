# maligeeAi - API Contracts & Backend Plan

## A. API Contracts

### 1. Auth Endpoints (Mock/Placeholder)
Since this is a landing page clone, auth buttons are UI-only. But we'll create placeholder endpoints:

```
POST /api/auth/google    → { message: "Google auth placeholder" }
POST /api/auth/github    → { message: "GitHub auth placeholder" }
POST /api/auth/email     → { email: string } → { message: "Email auth placeholder" }
```

### 2. Showcase Items
```
GET /api/showcase → List[ShowcaseItem]
ShowcaseItem: { id, mobile_image, laptop_image }
```

### 3. Features
```
GET /api/features → List[Feature]
Feature: { id, icon, title, description, mockup_type }
```

### 4. Stats
```
GET /api/stats → { users_count: string, description: string }
```

### 5. Contact/Waitlist (functional)
```
POST /api/waitlist → { email: string, name?: string } → { id, email, name, created_at }
GET  /api/waitlist/count → { count: int }
```

## B. Mock Data to Replace
- `mockData.js` → `showcaseItems` → from `/api/showcase`
- `mockData.js` → `features` → from `/api/features`
- `mockData.js` → `stats` → from `/api/stats`
- Waitlist form will be new functionality (CTA "Get Started Free" → email collection)

## C. Backend Implementation
1. MongoDB models: ShowcaseItem, Feature, Stats, WaitlistEntry
2. Seed endpoint to populate showcase/features/stats
3. Waitlist CRUD (create entry, get count)
4. CORS already configured

## D. Frontend-Backend Integration
- Replace static mock imports with `axios.get(API + '/showcase')` etc.
- Add waitlist modal to "Get Started Free" button
- Use `useEffect` + `useState` to load data from API
- Fallback to mock data if API fails
