"""Domen darajasidagi umumiy xatoliklar (HTTP'ga bog'lanmagan)."""


class AppError(Exception):
    """Barcha ilova xatoliklarining asosi."""

    status_code: int = 400
    detail: str = "Ilovada xatolik yuz berdi"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    detail = "Topilmadi"


class ConflictError(AppError):
    status_code = 409
    detail = "Ziddiyat: resurs allaqachon mavjud"


class AuthError(AppError):
    status_code = 401
    detail = "Autentifikatsiya xatosi"


class PermissionError(AppError):  # noqa: A001 (built-in bilan atayin bir xil nomlanadi)
    status_code = 403
    detail = "Ruxsat yo'q"


class RateLimitError(AppError):
    status_code = 429
    detail = "Juda ko'p urinish. Keyinroq qayta urinib ko'ring"
