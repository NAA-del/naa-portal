# NAA Portal Style Guide

## Terminology Standards

| Concept | Use This | Never Use |
|---------|----------|-----------|
| People | "Member" (in UI), "User" (in code) | "Client", "Customer" |
| Leadership | "Executive" or "EXCO" | "Leader", "Admin" |
| Groups | "Committee" | "Team", "Group", "Board" |
| Messages | "Announcement" | "News", "Update", "Post", "Notice" |
| Education | "CPD" (full: Continuing Professional Development) | "Training", "Course" |
| Portal Sections | "Member Hub", "Student Hub" | "Dashboard", "Portal" |

## Code Naming Conventions

### Python (.py files)
- Variables: `snake_case` (user_profile, committee_name)
- Functions: `snake_case` (get_user_profile, send_email)
- Classes: `PascalCase` (User, Committee, Announcement)
- Constants: `UPPER_SNAKE_CASE` (MAX_FILE_SIZE, DEFAULT_TIER)

### Templates (.html files)
- Variables: `snake_case` ({{ user.first_name }})
- CSS classes: Follow Medicio theme conventions
- Custom classes: `kebab-case` (member-card, student-profile)

### URLs
- Paths: `kebab-case` ('/member-id/', '/cpd-tracker/')
- Names: `snake_case` (name='member_id', name='cpd_tracker')

### Database
- Table names: `lowercase_plural` (users, committees, announcements)
- Field names: `snake_case` (first_name, date_joined, is_verified)