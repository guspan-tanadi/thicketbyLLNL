# Copyright 2022 Lawrence Livermore National Security, LLC and other
# Thicket Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: MIT

import numpy as np

from ..utils import verify_thicket_structures


def mean(thicket, columns=None):
    """Calculate the mean for each node in the performance data table.

    Designed to take in a thicket, and append one or more columns to the
    aggregated statistics table for the mean calculation for each node.

    Arguments:
        thicket (thicket): Thicket object
        columns (list): List of hardware/timing metrics to perform mean calculation on.
            Note, if using a columnar joined thicket a list of tuples must be passed in
            with the format (column index, column name).
    """
    if columns is None:
        raise ValueError(
            "To see a list of valid columns, run 'Thicket.performance_cols'."
        )

    verify_thicket_structures(thicket.dataframe, index=["node"], columns=columns)

    # thicket object without columnar index
    if thicket.dataframe.columns.nlevels == 1:
        df = thicket.dataframe[columns].reset_index().groupby("node").agg(np.mean)
        for column in columns:
            thicket.statsframe.dataframe[column + "_mean"] = df[column]
            # check to see if exclusive metric
            if column in thicket.exc_metrics:
                thicket.statsframe.exc_metrics.append(column + "_mean")
            # check to see if inclusive metric
            else:
                thicket.statsframe.inc_metrics.append(column + "_mean")
    # columnar joined thicket object
    else:
        df = (
            thicket.dataframe[columns].reset_index(level=1).groupby("node").agg(np.mean)
        )
        for idx, column in columns:
            thicket.statsframe.dataframe[(idx, column + "_mean")] = df[(idx, column)]
            # check to see if exclusive metric
            if (idx, column) in thicket.exc_metrics:
                thicket.statsframe.exc_metrics.append((idx, column + "_mean"))
            # check to see if inclusive metric
            else:
                thicket.statsframe.inc_metrics.append((idx, column + "_mean"))

        # sort columns in index
        thicket.statsframe.dataframe = thicket.statsframe.dataframe.sort_index(axis=1)
