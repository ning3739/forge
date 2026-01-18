.. image:: ../assets/logo.svg
   :align: center
   :width: 400px
   :alt: Forge Logo

.. raw:: html

   <p align="center">
     <a href="https://badge.fury.io/py/ningfastforge"><img src="https://badge.fury.io/py/ningfastforge.svg" alt="PyPI version"></a>
     <a href="https://pypi.org/project/ningfastforge/"><img src="https://img.shields.io/pypi/pyversions/ningfastforge.svg" alt="Python Versions"></a>
     <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
   </p>

----

Forge is a CLI tool that generates production-ready FastAPI projects. It collects your preferences through an interactive terminal interface, saves them to a configuration file, then generates a complete project structure with all the boilerplate code you need.

.. code-block:: bash

   pip install ningfastforge
   forge init

Why Forge?
----------

Every time you start a new FastAPI project, do you find yourself repeating the same tasks?

- Setting up database connections and ORM configuration
- Implementing JWT authentication and user management
- Integrating Redis caching and Celery task queues
- Writing Docker and deployment configurations
- Configuring test frameworks and CI/CD pipelines

**Forge was built to solve this problem.**

As a FastAPI developer, I got tired of building the same infrastructure from scratch for every new project. While there are many templates available online, they're either too simple or too complex to customize.

Forge's design philosophy:

- **Generate on demand**: Only generate what you need, nothing more, nothing less
- **Production-ready**: Generated code follows best practices and is ready for production
- **Easy to understand**: Clean code structure that's easy to maintain and extend
- **Quick start**: Go from zero to a complete project skeleton in minutes

Features
--------

- **Database Support**: PostgreSQL, MySQL, SQLite with SQLModel or SQLAlchemy ORM
- **Authentication**: JWT-based auth with two modes (basic or complete with email verification)
- **Caching**: Redis integration for caching and session management
- **Background Tasks**: Celery with Redis broker for async task processing
- **Testing**: Pre-configured pytest with async support
- **Deployment**: Docker and Docker Compose configurations
- **Migrations**: Alembic database migrations

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting-started/installation
   getting-started/quickstart
   getting-started/first-project

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user-guide/configuration
   user-guide/database
   user-guide/authentication
   user-guide/redis-caching
   user-guide/celery-tasks
   user-guide/testing
   user-guide/deployment
   user-guide/best-practices

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

   developer-guide/development-setup
   developer-guide/creating-generators
   developer-guide/adding-features

.. toctree::
   :maxdepth: 1
   :caption: Additional

   changelog

Links
-----

- **GitHub**: `ning3739/forge <https://github.com/ning3739/forge>`_
- **PyPI**: `ningfastforge <https://pypi.org/project/ningfastforge/>`_
- **Issues**: `Report bugs <https://github.com/ning3739/forge/issues>`_
