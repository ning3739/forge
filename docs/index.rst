Forge Documentation
===================

.. image:: ../assets/logo.svg
   :align: center
   :width: 480px
   :alt: Forge Logo

|

.. image:: https://badge.fury.io/py/ningfastforge.svg
   :target: https://badge.fury.io/py/ningfastforge
   :alt: PyPI version
   :align: center

.. image:: https://img.shields.io/pypi/pyversions/ningfastforge.svg
   :target: https://pypi.org/project/ningfastforge/
   :alt: Python Versions
   :align: center

.. image:: https://static.pepy.tech/badge/ningfastforge
   :target: https://pepy.tech/project/ningfastforge
   :alt: Downloads
   :align: center

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT
   :align: center

----

Forge is a powerful command-line tool that helps you quickly bootstrap **production-ready FastAPI projects** with best practices, intelligent defaults, and a beautiful interactive interface.

✨ Key Features
---------------

- 🎨 **Beautiful Interactive UI** - Stunning terminal interface with gradient colors and smooth animations
- 🚀 **Smart Presets** - Carefully curated presets for testing, dev tools, deployment, and monitoring
- 🔐 **Authentication Ready** - Built-in support for JWT authentication (Basic & Complete)
- 🗄️ **Database Flexibility** - Support for PostgreSQL, MySQL, and SQLite with SQLModel/SQLAlchemy
- 🔴 **Redis Integration** - Built-in Redis support for caching, sessions, and message queues
- 📋 **Background Tasks** - Celery integration with Redis broker for async task processing
- 💾 **Database Backup** - Automated database backup tasks supporting all database types
- 📦 **Modular Architecture** - Choose only the features you need
- 🧪 **Testing Built-in** - Pre-configured pytest with async support and coverage
- 🐳 **Docker Ready** - Production-ready Docker and Docker Compose configurations
- 🔍 **Type Safe** - Full type hints throughout generated code
- ⚡ **Async First** - Optimized for FastAPI's async capabilities

Quick Start
-----------

Get started with Forge in just a few commands:

.. code-block:: bash

   # Install from PyPI
   pip install ningfastforge

   # Create your first project (interactive mode)
   forge init

   # Navigate to project and run
   cd my-project
   uv sync
   uv run uvicorn app.main:app --reload

Visit ``http://127.0.0.1:8000/docs`` to see your API documentation!

What You Get
------------

When you create a project with Forge, you get:

- ✅ Fully structured FastAPI application
- ✅ Database models and migrations (Alembic)
- ✅ JWT authentication with user management
- ✅ CRUD operations and API routers
- ✅ Redis caching and session management
- ✅ Celery background tasks and scheduling
- ✅ Docker and Docker Compose configuration
- ✅ Comprehensive test suite with pytest
- ✅ Development tools (Black, Ruff)
- ✅ Environment configuration files
- ✅ Complete documentation and examples

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting-started/installation
   getting-started/quickstart
   getting-started/first-project

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user-guide/cli-commands
   user-guide/configuration
   user-guide/database
   user-guide/authentication
   user-guide/testing
   user-guide/deployment

.. toctree::
   :maxdepth: 2
   :caption: Architecture

   architecture/overview
   architecture/generator-system

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/config-reader
   api/generator-decorator
   api/orchestrator

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide

   developer-guide/creating-generators

.. toctree::
   :maxdepth: 1
   :caption: Additional Information

   changelog

Community and Support
---------------------

- **GitHub**: `ning3739/forge <https://github.com/ning3739/forge>`_
- **PyPI**: `ningfastforge <https://pypi.org/project/ningfastforge/>`_
- **Issues**: `Report bugs or request features <https://github.com/ning3739/forge/issues>`_

License
-------

Forge is released under the `MIT License <https://opensource.org/licenses/MIT>`_.

----

Made with ❤️ for the FastAPI community

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
