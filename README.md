# Issue Tracker

An issue tracking website created using the Django web framework.

## Applications

### Accounts

The accounts app builds on top of Django's user model to implement standard user functionality, such as registration, account management and password reset via email; and several different user types: *admin*, *project manager*, *developer* and *user*, to provide access control.

Registered accounts default to the user role, which represents an external consumer of the firm's services, and can be promoted to any other role, which represent different grades within the firm, by any admin.

**User Permissions:**

* Accounts:
    * View own account
    * Edit own account (excluding role)
    * Change/reset own password
* Comments:
    * Add comments to all active tickets
* Notifications:
    * View own notifications
* Projects:
    * View all active projects
    * View all archived projects
* Tickets:
    * View all tickets
    * Create tickets in all active projects

**Developer Permissions:**

All user permissions, and:

* Tickets:
    * Close assigned tickets
    * Edit assigned tickets

**Project Manager Permissions:**

All developer permissions, and:

* Projects:
    * Archive assigned projects
    * Edit assigned projects
    * Create new projects
* Tickets:
    * Close all tickets in assigned projects
    * Edit all tickets in assigned projects

**Admin Permissions:**

All project manager permissions, and:

* Accounts:
    * View all accounts
    * Edit all accounts' role
* Projects:
    * Archive all projects
    * Edit all projects
    * Remove all projects
* Tickets:
    * Close all tickets
    * Edit all tickets
    * Remove all tickets

### Comments

Comments may be added to any active ticket, and serve as a means of communication between the involved parties following ticket creation.

### Notifications

This website has a built-in notification system, which sends appropriate notifications whenever key actions are performed. For example, project managers receive a notification whenever a new ticket is created in one of their projects, prompting them to process the ticket and assign it to a developer; whereas users receive notifications whenever their created tickets are updated, or a new comment has been added.

### Projects

Projects are a collection of tickets which represent any service the firm is working, or has worked, on. Each project has a project manager who is responsible for managing the project and processing all new tickets.

Projects can be active or archived. All assets within an archived project, including the project itself, are read-only.

### Tickets

Tickets represent individual issues, feature requests and comments relating to a specific project.
