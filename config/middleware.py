import json

import structlog
from django.utils.deprecation import MiddlewareMixin

logger = structlog.getLogger("default")


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log failed requests for later analysis.

    This middleware captures the body of incoming requests and logs details of
    responses with status codes indicating errors (excluding certain statuses) to
    the FailedRequest model.
    """

    def process_request(self, request):
        """
        Capture the body of the incoming request and store it in a custom attribute.

        Args:
            request (HttpRequest): The incoming HTTP request.
        """
        request._body = request.body

    def process_response(self, request, response):
        """
        Log details of failed responses to the FailedRequest model, excluding specific statuses.

        Args:
            request (HttpRequest): The incoming HTTP request.
            response (HttpResponse): The outgoing HTTP response.

        Returns:
            HttpResponse: The unmodified response object.
        """

        try:
            exclude_status = [401, 404]
            if (
                response.status_code >= 400
                and response.status_code not in exclude_status
                and request.headers.get("content-type", "application/json") == "application/json"
            ):
                logger.error(
                    f"API Request failed with status code {response.status_code}",
                    request_data=json.loads(request._body) if request._body else None,
                    request_method=request.method,
                    request_path=request.path,
                    request_query_params=dict(request.GET),
                    remote_addr=request.META.get("REMOTE_ADDR"),
                    response_status_code=response.status_code,
                    request_id=request.headers.get("X-Request-ID", None),
                    user_id=(str(request.user.id) if request.user.is_authenticated else None),
                )
        except:
            logger.error(  # noqa: TRY400
                f"API Request failed with status code {response.status_code}",
                request_data=request._body,
                request_method=request.method,
                request_path=request.path,
                request_query_params=dict(request.GET),
                remote_addr=request.META.get("REMOTE_ADDR"),
                response_status_code=response.status_code,
                request_id=request.headers.get("X-Request-ID", None),
                user_id=str(request.user.id) if request.user.is_authenticated else None,
            )
        finally:
            # add x request id
            response["X-Request-ID"] = request.headers.get("X-Request-ID", None)
            return response  # noqa: B012


class IPLoggingMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        try:
            logger.info(
                f"API Request completed with status code {response.status_code}",
                request_method=request.method,
                request_path=request.path,
                ip_address=(
                    request.META.get("HTTP_X_FORWARDED_FOR")
                    if request.META.get("HTTP_X_FORWARDED_FOR")
                    else request.META.get("REMOTE_ADDR")
                ),
                response_status_code=response.status_code,
                request_id=request.headers.get("X-Request-ID", None),
                user_id=(str(request.user.id) if request.user.is_authenticated else None),
            )
        except Exception:
            pass

        return response
