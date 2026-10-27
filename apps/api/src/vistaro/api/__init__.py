"""HTTP api layer.

Feature routers live here; each module mounts its routers from
:mod:`vistaro.main`. This layer may import ``vistaro.core``, ``vistaro.db``
and ``vistaro.services`` but never becomes an import dependency of them
(import-linter contract).
"""
