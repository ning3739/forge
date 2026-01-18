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
