import pprint
from enum import Enum
from typing import Any, Dict, Type


class StrictMode(Enum):
    FULL_STRICT = "FULL_STRICT"
    TYPE_STRICT = "TYPE_STRICT"
    STRICT_NOT_NULL = "STRICT_NOT_NULL"
    UNSTRICT_TO_STRING = "UNSTRICT_TO_STRING"
    UNSTRICT_TO_BYTES = "UNSTRICT_TO_BYTES"
    UNSTRICT = "UNSTRICT"

    @classmethod
    def parse(cls, strict_val: Any) -> "StrictMode":
        if isinstance(strict_val, StrictMode):
            return strict_val
        if strict_val is True:
            return cls.FULL_STRICT
        if strict_val is False:
            return cls.UNSTRICT
        try:
            return cls(strict_val)
        except ValueError:
            return cls.UNSTRICT


class DTOValidator:
    @staticmethod
    def _check_type(v: Any, expected_type: Type) -> bool:
        if type(v) is expected_type:
            return True
        try:
            if isinstance(v, expected_type):
                return True
        except TypeError:
            pass
        return False

    @staticmethod
    def _validate_exact_keys(dict_object: Dict[str, Any], dto_fields: Dict[str, Type]) -> None:
        if set(dto_fields.keys()) != set(dict_object.keys()):
            raise Exception(
                f"Mismatched fields: Query result and DTO structure do not align.\n\nIn row: {pprint.pformat(dict_object)}\n\nIn DTO: {pprint.pformat(dto_fields)}"
            )

    @classmethod
    def _validate_types(cls, dict_object: Dict[str, Any], dto_fields: Dict[str, Type], allow_null: bool = True) -> None:
        for k, v in dict_object.items():
            if v is None:
                if not allow_null:
                    raise Exception(f"Field '{k}' cannot be Null/None in STRICT_NOT_NULL mode.")
                continue

            if not cls._check_type(v, dto_fields[k]):
                raise Exception(
                    f"Type mismatch for field '{k}': expected {dto_fields[k]}, got {type(v)} (value: {v})"
                )

    @staticmethod
    def _remove_extra_keys(dict_object: Dict[str, Any], dto_fields: Dict[str, Type]) -> None:
        for k in list(dict_object.keys()):
            if k not in dto_fields:
                dict_object.pop(k)

    @classmethod
    def process(
        cls, dict_object: Dict[str, Any], dto_fields: Dict[str, Type], mode: StrictMode
    ) -> None:
        """Validates and transforms the dict_object in-place according to the strictness mode."""
        if mode == StrictMode.FULL_STRICT:
            cls._validate_exact_keys(dict_object, dto_fields)
            cls._validate_types(dict_object, dto_fields, allow_null=True)

        elif mode == StrictMode.STRICT_NOT_NULL:
            cls._validate_exact_keys(dict_object, dto_fields)
            cls._validate_types(dict_object, dto_fields, allow_null=False)

        elif mode in (StrictMode.TYPE_STRICT, StrictMode.TYPE_SCRICT):
            cls._remove_extra_keys(dict_object, dto_fields)
            cls._validate_types(dict_object, dto_fields, allow_null=True)

        elif mode == StrictMode.UNSTRICT_TO_STRING:
            cls._remove_extra_keys(dict_object, dto_fields)
            for k, v in dict_object.items():
                dict_object[k] = str(v) if v is not None else None

        elif mode == StrictMode.UNSTRICT_TO_BYTES:
            cls._remove_extra_keys(dict_object, dto_fields)
            for k, v in dict_object.items():
                if v is None:
                    continue
                elif isinstance(v, bytes):
                    continue
                elif isinstance(v, str):
                    dict_object[k] = v.encode("utf-8")
                else:
                    dict_object[k] = str(v).encode("utf-8")

        else:
            cls._remove_extra_keys(dict_object, dto_fields)
