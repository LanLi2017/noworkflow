# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# Copyright (c) 2016 Polytechnic Institute of New York University.
# This file is part of noWorkflow.
# Please, consult the license terms in the LICENSE file.
"""Slicing Dependency Model"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

from sqlalchemy import Column, Integer
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint

from ...utils.prolog import PrologDescription, PrologTrial, PrologAttribute

from .base import AlchemyProxy, proxy_class, backref_one


@proxy_class
class SlicingDependency(AlchemyProxy):
    """Represent a variable dependency captured during program slicing"""

    __tablename__ = "slicing_dependency"
    __table_args__ = (
        PrimaryKeyConstraint("trial_id", "id"),
        ForeignKeyConstraint(["trial_id"],
                             ["trial.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id", "dependent_activation_id"],
                             ["function_activation.trial_id",
                              "function_activation.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id", "supplier_activation_id"],
                             ["function_activation.trial_id",
                              "function_activation.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id",
                              "dependent_activation_id",
                              "dependent_id"],
                             ["slicing_variable.trial_id",
                              "slicing_variable.activation_id",
                              "slicing_variable.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id",
                              "supplier_activation_id",
                              "supplier_id"],
                             ["slicing_variable.trial_id",
                              "slicing_variable.activation_id",
                              "slicing_variable.id"], ondelete="CASCADE"),
    )
    trial_id = Column(Integer, index=True)
    id = Column(Integer, index=True)                                             # pylint: disable=invalid-name
    dependent_activation_id = Column(Integer, index=True)
    dependent_id = Column(Integer, index=True)
    supplier_activation_id = Column(Integer, index=True)
    supplier_id = Column(Integer, index=True)

    trial = backref_one("_trial")  # Trial._slicing_dependencies
    # Activation._dependent_variables, SlicingVariable._suppliers_dependencies
    dependent_activation = backref_one("_dependent_activation")
    dependent = backref_one("_dependent")
    # Activation._supplier_variables, SlicingVariable._dependents_dependencies
    supplier_activation = backref_one("_supplier_activation")
    supplier = backref_one("_supplier")

    prolog_description = PrologDescription("dependency", (
        PrologTrial("trial_id"),
        PrologAttribute("id"),
        PrologAttribute("dependent_activation_id"),
        PrologAttribute("dependent_id"),
        PrologAttribute("supplier_activation_id"),
        PrologAttribute("supplier_id"),
    ))

    def __repr__(self):
        return (
            "SlicingDependency({0.trial_id}, {0.id}, "
            "{0.dependent}, {0.supplier})"
        ).format(self)

    def __str__(self):
        return "{0.dependent} <- {0.supplier}".format(self)
