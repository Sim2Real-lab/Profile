You are an expert full-stack Django developer and deployment engineer.

I need you to build a complete production-ready **Member Proforma Generation System** for Robotech NITK.

## 1. Existing Infrastructure

There is already an existing website:

`https://robotech.nitk.ac.in`

The server is an existing Linux VM managed by NITK, with Nginx already configured.

I do NOT control the DNS for `nitk.ac.in`, so DO NOT create or require a subdomain.

The new application must be accessible at:

`https://robotech.nitk.ac.in/proforma/`

The architecture should be:

Internet
→ Nginx
→ `/proforma/`
→ Django application on `127.0.0.1:8001`

The existing Robotech website MUST NOT be broken or modified unnecessarily.

The Proforma application should be an independent Django project/application running alongside the existing website.

Do not introduce unnecessary infrastructure.

## 2. Technology Requirements

Use:

- Python 3.x
- Django
- Django Templates
- HTML5
- CSS3
- Bootstrap 5
- JavaScript only where required
- PostgreSQL if an existing PostgreSQL server/database is available
- SQLite as a fallback for development
- Pillow for image handling
- WeasyPrint for PDF generation
- Python `qrcode` package for QR generation

Do NOT use React unless absolutely necessary.

Do NOT create a separate frontend application.

Do NOT require another VM.

Do NOT require another domain.

Do NOT require Docker unless it is necessary for the existing server environment.

Keep the architecture simple and maintainable.

---

# 3. Application URL

The application must work correctly under:

`/proforma/`

not at the root `/`.

Configure Django correctly for this deployment.

Use an appropriate configuration such as:

`FORCE_SCRIPT_NAME = "/proforma"`

and make sure all:

- static URLs
- media URLs
- form actions
- redirects
- login URLs
- PDF URLs
- admin URLs

work correctly under `/proforma/`.

Do not hardcode `/` where Django URL reversing should be used.

---

# 4. Main User Flow

The user visits:

`https://robotech.nitk.ac.in/proforma/`

They see a professional member information form.

They fill it out and submit it.

After submission:

1. Validate all data.
2. Save the member to the database.
3. Save the uploaded photo.
4. Generate a unique member ID.
5. Generate a username.
6. Generate a short random password.
7. Generate a QR code.
8. Generate a professional A4 PDF.
9. Save the generated PDF.
10. Show a success page.
11. Allow the user to download the generated PDF.

The complete process should happen automatically.

---

# 5. Form Fields

The form must contain:

## Personal Information

- Full Name
- Roll Number
- Branch
- Date of Birth
- Phone Number
- Email
- Photo

## Social Media

- LinkedIn
- Instagram

## Club Information

SIG selection:

- EC&P
- Design
- Website
- Marketing
- Media

Previous Core:

- Yes
- No

Are you part of Y26 Core?

- Yes
- No

## Skills

Skills must be dynamically displayed based on the selected SIG.

The user should be able to select multiple skills using checkboxes.

Use an initial configurable skill list such as:

### EC&P

- Electronics
- Arduino
- ESP32
- Raspberry Pi
- PCB Design
- Embedded Systems
- IoT
- Robotics
- Sensors
- Microcontrollers

### Design

- Figma
- Photoshop
- Illustrator
- Canva
- Blender
- UI/UX
- Motion Graphics
- 3D Design
- Graphic Design
- Video Design

### Website

- HTML
- CSS
- JavaScript
- Python
- Django
- React
- Node.js
- SQL
- MongoDB
- Git
- GitHub
- REST API
- UI/UX

### Marketing

- Social Media
- Content Writing
- SEO
- Branding
- Campaign Management
- Public Relations
- Event Marketing
- Copywriting
- Analytics

### Media

- Photography
- Videography
- Video Editing
- Premiere Pro
- After Effects
- DaVinci Resolve
- Cinematography
- Lightroom
- Motion Graphics

Make this skill configuration easy to modify later.

---

# 6. Projects

Add a "Projects Contributed" section.

The preferred UI is a repeatable project component.

Example:

Project 1:
- Project Name
- Contribution / Role

Button:

`+ Add Another Project`

Allow the user to add multiple projects.

Store this properly in the database rather than forcing everything into one giant text field.

---

# 7. Reflection Questions

Add two large text areas.

### Question 1

"What have you learnt from the club?"

### Question 2

"What changes would you like to see or implement in the club?"

Both should be required.

---

# 8. Form UX

Make the form professional and easy to fill.

Prefer a multi-step form:

### Step 1
Personal Information

### Step 2
Club Information & Skills

### Step 3
Projects & Contributions

### Step 4
Reflection

### Step 5
Review & Submit

Show a progress indicator.

Allow:

- Previous
- Next
- Save/continue if practical
- Review before submitting

Validate fields on both frontend and backend.

Do NOT rely only on JavaScript validation.

---

# 9. Photo Upload

The photo should:

- Accept JPG/JPEG/PNG
- Validate file type
- Validate file size
- Resize/crop appropriately
- Maintain reasonable quality
- Be suitable for placement in an A4 PDF

Use Pillow.

Prefer a fixed portrait crop for the PDF.

---

# 10. Member ID

Generate a unique member ID automatically.

Use a configurable format.

Example:

`RBT26-23MI001`

The exact schema should be configurable in one place.

Do NOT rely on the user entering their own member ID.

Ensure uniqueness.

---

# 11. Username

Generate the username automatically using a predictable schema.

Example:

`RBT26-23MI001`

or another clean configurable schema.

The username must be unique.

Do not ask the user to create it manually.

---

# 12. Password

Generate a short random password.

It should be easy enough to print and manually type.

Example:

`K7p4X9`

or:

`R8m2Q6`

Use approximately 6–8 characters.

Avoid confusing characters such as:

- O / 0
- I / l / 1

Store only the secure password hash in the database.

The plaintext password should only be available during the credential-generation process and for the generated PDF.

Do not unnecessarily expose passwords in admin lists.

---

# 13. QR Code

Generate a QR code for every member.

Preferred approach:

The QR should contain a secure member URL/token rather than directly storing the password in plaintext.

Example:

`https://robotech.nitk.ac.in/proforma/member/<secure-token>/`

The token must be cryptographically secure and non-guessable.

When scanned, it should take the user to the appropriate member/authentication page.

Design the system so the QR implementation can later be changed to support actual member login.

The generated PDF should contain the QR code.

---

# 14. PDF Generation

Generate a professional A4 PDF automatically after submission.

Use WeasyPrint with an HTML/CSS template.

Do NOT manually draw every PDF element if HTML/CSS can be used.

The PDF should look like an official Robotech NITK member proforma.

Include:

- Robotech NITK branding
- Member photo
- Name
- Roll Number
- Branch
- DOB
- Phone
- Email
- LinkedIn
- Instagram
- SIG
- Previous Core status
- Y26 Core status
- Selected skills
- Projects contributed
- Learning review
- Suggested changes/review
- Member ID
- Username
- Password
- QR code

Use a clean professional layout.

Avoid excessive colors, gradients, glowing effects, or unnecessary decoration.

Make sure long reviews and project lists flow correctly across pages.

The PDF must remain readable when printed.

Use A4 dimensions.

---

# 15. PDF Security

Do not expose generated PDFs through predictable public URLs.

PDF downloads should preferably be protected through Django.

For example:

User submits form
→ PDF generated
→ success page
→ authenticated/authorized download

Do not make the entire generated PDF directory publicly browseable.

---

# 16. Database Design

Create clean Django models.

At minimum:

### Member

Fields:

- id
- member_id
- name
- roll_no
- branch
- dob
- phone
- email
- photo
- linkedin
- instagram
- sig
- previous_core
- y26_core
- learning_review
- changes_review
- username
- password_hash / Django authentication relationship
- qr/token information
- pdf
- created_at
- updated_at

### Skill

Create a configurable skill model.

Fields can include:

- name
- sig
- active

### MemberSkill

Many-to-many relationship between Member and Skill.

### Project

Fields:

- member
- project_name
- contribution
- created_at

Use proper relational database design.

Do not store projects and skills as comma-separated strings.

---

# 17. Authentication

Use Django authentication where appropriate.

Create a separate admin/staff area.

Do not expose the Django admin unnecessarily to public users.

The admin should be able to manage member records.

---

# 18. Admin Dashboard

Create a useful admin dashboard.

It should allow staff to:

- View all members
- Search by name
- Search by roll number
- Filter by SIG
- Filter by previous Core status
- Filter by Y26 Core status
- View complete member profile
- Download PDF
- Regenerate PDF
- Edit member
- Delete member
- Export data

Add a CSV export.

If practical, add bulk PDF generation/download.

---

# 19. Duplicate Handling

Roll number should be unique unless there is a strong reason otherwise.

Email should be validated.

Phone should be validated.

If someone tries to submit the same roll number again, do not silently create a duplicate member.

Show a useful error.

Allow authorized staff to edit/re-submit when necessary.

---

# 20. Security Requirements

Implement:

- CSRF protection
- Django authentication
- Secure password hashing
- File upload validation
- File size limits
- Input validation
- XSS-safe rendering
- SQL injection protection through Django ORM
- Secure random tokens
- Secure cookies
- Appropriate production settings

Never trust client-side validation.

Never directly interpolate user input into SQL.

Never store passwords in plaintext in the database.

---

# 21. Nginx Deployment

The application must run locally on:

`127.0.0.1:8001`

Nginx should expose it through:

`https://robotech.nitk.ac.in/proforma/`

Provide the exact Nginx configuration required.

The configuration must NOT replace the existing Robotech server block.

Add only the required `/proforma/` routing.

For example, the conceptual flow is:

`location /proforma/`

→ proxy to

`http://127.0.0.1:8001`

Make sure:

- WebSocket configuration is not added unless required.
- Static files work.
- Media/PDF downloads work.
- HTTPS works.
- Existing Robotech routes continue working.

---

# 22. Django Production Configuration

Prepare the project for production.

Include:

- `.env` support
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- database credentials
- media configuration
- static configuration
- secure cookie settings
- CSRF trusted origins

Do NOT hardcode secrets.

Provide `.env.example`.

---

# 23. Process Management

Use Gunicorn for production.

Example:

`127.0.0.1:8001`

Create a systemd service such as:

`robotech-proforma.service`

The service should:

- Start Django/Gunicorn
- Restart on failure
- Start on boot
- Run under an appropriate non-root user where possible

Provide exact commands to install and configure it.

---

# 24. Static and Media

Use:

`STATIC_ROOT`

and:

`MEDIA_ROOT`

Run:

`python manage.py collectstatic`

Configure Nginx appropriately.

However, sensitive generated PDFs should still be served through Django authorization rather than blindly exposing the entire PDF directory.

---

# 25. Project Structure

Use a clean structure similar to:

robotech-proforma/
│
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── members/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── services/
│   │   ├── credentials.py
│   │   ├── qr.py
│   │   └── pdf.py
│   └── ...
│
├── templates/
│
├── static/
│
├── media/
│
└── generated/
```

Keep business logic out of views where practical.

---

# 26. UI Design

The UI should feel like an official Robotech NITK system.

Use:

- Clean white/light background
- Professional typography
- Robotech branding
- Subtle accent colors
- Good spacing
- Responsive layout
- Mobile-friendly form
- Accessible labels
- Clear error messages

Avoid:

- Gradients
- Excessive animations
- Glowing backgrounds
- Excessive rounded cards
- Unnecessary decorative elements

The form should work well on both desktop and mobile.

---

# 27. Success Page

After successful submission show:

"Proforma generated successfully."

Display:

- Member ID
- Username
- Password

Then provide:

`Download Proforma PDF`

Also warn the user to save/print the generated credentials.

Do not expose credentials again unnecessarily after leaving the page.

---

# 28. Error Handling

Implement proper error pages for:

- Invalid form
- Invalid photo
- PDF generation failure
- Database failure
- Unauthorized PDF access
- Invalid QR/token
- Missing member

Do not expose stack traces in production.

Log server-side errors.

---

# 29. Logging

Configure useful application logging.

Log:

- Submission success/failure
- PDF generation errors
- Authentication failures
- Admin actions where appropriate

Do NOT log passwords.

Do NOT log sensitive credentials.

---

# 30. Deliverables

I want you to actually generate the complete project, not merely explain it.

Provide:

1. Complete Django project
2. All Python files
3. All HTML templates
4. CSS
5. JavaScript
6. Database models
7. Forms
8. Views
9. URLs
10. Admin dashboard
11. PDF generation
12. QR generation
13. Credential generation
14. Photo upload
15. Migrations
16. Requirements file
17. `.env.example`
18. Production settings
19. Gunicorn configuration
20. systemd service
21. Nginx configuration
22. README
23. Database setup instructions
24. Deployment instructions
25. Testing instructions

Do not give pseudo-code where actual code is required.

---

# 31. Deployment Instructions

The README must contain exact commands for a fresh Ubuntu server.

Include:

- Creating virtual environment
- Installing dependencies
- Installing system packages required by WeasyPrint
- Configuring PostgreSQL
- Running migrations
- Creating superuser
- Collecting static files
- Testing Gunicorn
- Creating systemd service
- Configuring Nginx
- Testing Nginx
- Reloading Nginx
- Checking logs
- Troubleshooting

Assume the existing Nginx server already serves:

`robotech.nitk.ac.in`

Do not overwrite its configuration.

---

# 32. Development First

Build the system incrementally.

First ensure:

`/proforma/`

loads.

Then:

1. Form works.
2. Data saves.
3. Photo uploads.
4. Skills work dynamically.
5. Projects work.
6. Credentials generate.
7. QR generates.
8. PDF generates.
9. PDF downloads.
10. Admin works.
11. Production deployment works.

Do not attempt to solve everything with an unnecessarily complex architecture at once.

---

# 33. Important Constraint

This application is being built urgently.

Prioritize:

1. Reliability
2. Simplicity
3. Ease of deployment
4. Maintainability
5. Professional UI

Avoid unnecessary libraries and infrastructure.

If a requirement can be implemented using native Django functionality, prefer native Django.

---

# 34. Final Requirement

At the end, I should be able to open:

`https://robotech.nitk.ac.in/proforma/`

fill the form, submit it, and automatically receive a professionally formatted A4 PDF containing all submitted information, generated credentials, and QR code.

The existing `robotech.nitk.ac.in` website must continue functioning exactly as before.

Before making deployment changes, inspect the existing project/server configuration and explicitly identify anything that could conflict with the new `/proforma/` application.

Do not overwrite existing Nginx configuration blindly.
Do not change DNS.
Do not change the existing Robotech application unless required.

**One recommendation:** give this prompt to an agent that has **terminal/server access**, not just a chat-only coding model. The important part here is that it needs to inspect the existing Nginx configuration and actually deploy/test the `/proforma/` route.