"""
==================================================
TechSoul AI
API Response Service
==================================================

Provides standardized JSON responses
for all backend API endpoints.
"""

from flask import jsonify


class APIResponse:
    """
    Standard API Response Helper
    """

    @staticmethod
    def success(message="", data=None, status=200):
        """
        Success Response

        Parameters
        ----------
        message : str
            Success message

        data : dict
            Response payload

        status : int
            HTTP status code
        """

        if data is None:
            data = {}

        response = {

            "success": True,

            "message": message,

            "data": data

        }

        return jsonify(response), status

    @staticmethod
    def error(message="", status=400):
        """
        Error Response

        Parameters
        ----------
        message : str
            Error message

        status : int
            HTTP status code
        """

        response = {

            "success": False,

            "message": message,

            "data": {}

        }

        return jsonify(response), status

    @staticmethod
    def validation(errors):
        """
        Validation Error Response

        Parameters
        ----------
        errors : list
            List of validation errors
        """

        response = {

            "success": False,

            "message": "Validation Failed",

            "errors": errors,

            "data": {}

        }

        return jsonify(response), 422

    @staticmethod
    def not_found(message="Resource not found"):
        """
        Resource Not Found Response
        """

        response = {

            "success": False,

            "message": message,

            "data": {}

        }

        return jsonify(response), 404

    @staticmethod
    def server_error(message="Internal Server Error"):
        """
        Internal Server Error Response
        """

        response = {

            "success": False,

            "message": message,

            "data": {}

        }

        return jsonify(response), 500