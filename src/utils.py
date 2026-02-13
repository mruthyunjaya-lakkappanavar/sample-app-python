"""Utility functions — intentionally has lint issues for CI demo."""

import os, sys, json  # noqa: multiple imports on one line (lint error)

def   calculate_discount(price,discount):  # extra space, missing type hints
    """Calculate discounted price."""
    if discount>100 or discount<0:  # missing spaces around operators
        raise ValueError("Invalid discount")
    result=price-(price*discount/100)  # missing spaces
    return result


def     process_data( data ):  # extra spaces everywhere
    """Process data — deliberately messy."""
    items=[]  # no space around =
    for  item  in data:  # extra spaces
        if item!=None:  # should use 'is not None' + no spaces
            items.append(item)
    return items


def unused_function():
    """This function is never called — dead code."""
    x = 1
    y = 2
    z = x + y
    return z


class   BadlyFormattedClass:  # extra spaces
    """A poorly formatted class for lint demo."""
    def __init__(self,name,value):  # missing spaces after commas
        self.name=name  # missing spaces
        self.value=value

    def get_info( self ):  # extra space in params
        return {"name":self.name,"value":self.value}  # missing spaces after colons
