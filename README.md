# Library_management_system
Used to make the work of libarians more easier
# 📚 LibraryOS - Premium Library Management System

A modern, feature-rich library management system built with Django, featuring a stunning glassmorphic UI, automated fine calculation, and comprehensive book and member management.

![Django Version](https://img.shields.io/badge/Django-6.0.3-green.svg)
![Python Version](https://img.shields.io/badge/Python-3.13-blue.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### Core Features
- **Member Management** - Add, edit, delete, and manage library members
- **Book Catalog** - Complete book inventory management with genre classification
- **Borrow/Return System** - Issue books, track returns, and manage overdue items
- **Automated Fine Calculation** - ₹2 per day automatic fine after 7-day due date
- **Real-time Status Updates** - Automatic status changes for overdue books
- **Search & Filter** - Advanced search and filter capabilities for books and members
- **Premium UI/UX** - Glassmorphic design with dark theme and smooth animations

### Member Features
- Member registration with unique ID generation
- Membership type-based borrowing limits:
  - Student: 3 books
  - Faculty: 7 books
  - Staff: 5 books
  - Public: 2 books
- Member status tracking (Active/Suspended/Inactive)
- View borrowing history and current loans

### Book Features
- Complete book catalog with ISBN, genre, publisher, and year
- Track total and available copies
- Auto-update status based on availability
- Search by title, author, or ISBN

### Borrowing System
- Auto-calculation of due date (7 days from issue date)
- Real-time fine calculation (₹2/day after due date)
- Overdue tracking and alerts
- Return processing with automatic fine collection

### Premium UI
- Glassmorphic design with blur effects
- Animated background with floating particles
- Responsive layout for all devices
- Dark theme with gradient accents
- Interactive stat cards with hover effects
- Real-time form validation
- Popup message notifications

## 🚀 Tech Stack

- **Backend**: Django 6.0.3
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: MySQL / SQLite (configurable)
- **CSS Framework**: Custom premium design
- **Icons**: Font Awesome 6
- **Fonts**: Google Fonts (Syne, Inter)

## 📋 Prerequisites

- Python 3.13 or higher
- pip (Python package manager)
- MySQL (optional, can use SQLite)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/library-management-system.git
cd library-management-system
