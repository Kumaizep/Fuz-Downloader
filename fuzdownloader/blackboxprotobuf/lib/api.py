"""The `blackboxprotobuf.lib.api` module provides high level functions for
decoding and re-encoding protobuf messages.

Most functions take the input data, a type definition and a config object.

The 'message_type' or type definition (typedef) is a blackboxprotobuf specific format
which defines which types should be used for decoding/encoding each field. It
is optional for decoding functions but required for encoding funtions. The
decoding function will return a typedef that is require to re-encode the array.
If a typedef was provided during decoding, then those types will be used for
decoding and the typedef return will be the original typedef + any new fields
in the message.

The config argument is the Config object from `blackboxprotobuf.lib.config` and
allows reconfiguring default types and stores "known" message typedefs that can
be referenced within other typedefs. This argument can be left out to use a
default shared config object.
"""

# Copyright (c) 2018-2022 NCC Group Plc
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import six
import json
import collections
import blackboxprotobuf.lib.protofile
import blackboxprotobuf.lib.types.length_delim
import blackboxprotobuf.lib.types.type_maps
import blackboxprotobuf.lib.config
from blackboxprotobuf.lib.exceptions import TypedefException, EncoderException


def decode_message(buf, message_type=None, config=None):
    """Decode a protobuf message and return a python dictionary representing
    the message.

    Args:
        buf: Bytes representing an encoded protobuf message
        message_type: Optional type to use as the base for decoding. Allows for
            customizing field types or names. Can be a python dictionary or a
            message type name which maps to the `known_types` dictionary in the
            config. Defaults to an empty definition '{}'.
        config: `blackboxprotobuf.lib.config.Config` object which allows
            customizing default types for wire types and holds the
            `known_types` array. Defaults to
            `blackboxprotobuf.lib.config.default` if not provided.
    Returns:
        A tuple containing a python dictionary representing the message and a
        type definition for re-encoding the message.

        The type definition is based on the `message_type` argument if one was
        provided, but may add additional fields if new fields were encountered
        during decoding.
    """

    if config is None:
        config = blackboxprotobuf.lib.config.default

    if isinstance(buf, bytearray):
        buf = bytes(buf)
    buf = six.ensure_binary(buf)
    if message_type is None or isinstance(message_type, str):
        if message_type not in config.known_types:
            message_type = {}
        else:
            message_type = config.known_types[message_type]

    value, typedef, _, _ = blackboxprotobuf.lib.types.length_delim.decode_message(
        buf, config, message_type
    )
    return value, typedef


def encode_message(value, message_type, config=None):
    """Re-encode a python dictionary as a binary protobuf message.

    Args:
        value: Python dictionary to re-encode to bytes. This should usually be
            a modified version of the dictionary returned by `decode_message`.
        message_type: Type definition to use to re-encode the message. This
            will should generally be the type definition returned from the
            original `decode_message` call.
        config: `blackboxprotobuf.lib.config.Config` object which allows
            customizing default types for wire types and holds the
            `known_types` array. Defaults to
            `blackboxprotobuf.lib.config.default` if not provided.
    Returns:
        A bytearray containing the encoded protobuf message.
    """

    if config is None:
        config = blackboxprotobuf.lib.config.default
    return bytes(
        blackboxprotobuf.lib.types.length_delim.encode_message(
            value, config, message_type
        )
    )


def protobuf_to_json(*args, **kwargs):
    """Decode a protobuf message and return a JSON string representing the
    message.

    Args:
        buf: Bytes representing an encoded protobuf message
        message_type: Optional type to use as the base for decoding. Allows for
            customizing field types or names. Can be a python dictionary or a
            message type name which maps to the `known_types` dictionary in the
            config. Defaults to an empty definition '{}'.
        config: `blackboxprotobuf.lib.config.Config` object which allows
            customizing default types for wire types and holds the
            `known_types` array. Defaults to
            `blackboxprotobuf.lib.config.default` if not provided.
    Returns:
        A tuple containing a JSON string representing the message and a type
        definition for re-encoding the message.

        The JSON string and type definition are annotated and sorted for
        readability.

        The type definition is based on the `message_type` argument if one was
        provided, but may add additional fields if new fields were encountered
        during decoding.
    """
    value, message_type = decode_message(*args, **kwargs)
    value = _json_safe_transform(
        value, message_type, False, config=kwargs.get("config", None)
    )
    value = _sort_output(value, message_type, config=kwargs.get("config", None))
    _annotate_typedef(message_type, value)
    message_type = sort_typedef(message_type)
    return json.dumps(value, indent=2), message_type


def protobuf_from_json(json_str, message_type, *args, **kwargs):
    """Re-encode a JSON string as a binary protobuf message.

    Args:
        json_str: JSON string to re-encode to protobuf message bytes. This
            should usually be a modified version of the value returned by
            `protobuf_to_json`.
        message_type: Type definition to use to re-encode the message. This
            will should generally be the type definition returned from the
            original `protobuf_to_json` call.
        config: `blackboxprotobuf.lib.config.Config` object which allows
            customizing default types for wire types and holds the
            `known_types` array. Defaults to
            `blackboxprotobuf.lib.config.default` if not provided.
    Returns:
        A bytearray containing the encoded protobuf message.
    """
    value = json.loads(json_str)
    _strip_typedef_annotations(message_type)
    value = _json_safe_transform(value, message_type, True)
    return encode_message(value, message_type, *args, **kwargs)


def export_protofile(message_types, output_filename):
    """This function attempts to export a set of message type definitions to a
    `.proto` file for use with other tools.

    Args:
        message_types: Python dictionary containing the type definitions to
            export. The dictionary should contain the message type name as the
            key and the type definition as the value.
        output_filename: String representing the filename to output the
            protobuf definition file to.
    """
    blackboxprotobuf.lib.protofile.export_proto(
        message_types, output_filename=output_filename
    )


def import_protofile(input_filename, save_to_known=True, config=None):
    """This function attempts to import a set of message type definitions from a
    `.proto` file.

    This is a convenience function for `blackboxprotobuf.lib.protofile`. The
    protobuf file import support is not complete and may fail for some type
    definitions.

    Args:
        input_filename: Filename to read the protobuf definitions from.
        save_to_known: If True, this function will save the message type
            definitions to `config.known_types`. Otherwise, it will return them
            to the caller. Defaults to `True`.
        config: Optional config object which stores the `known_types` map.
            Defaults to `blackboxprotobuf.lib.config.default`.
    Returns:
        If `save_to_known` is False, then the type definitions read from the
        file are returned as a dictionary, with the type names as the keys and
        type definitions as the values.
    """
    if config is None:
        config = blackboxprotobuf.lib.config.default

    new_typedefs = blackboxprotobuf.lib.protofile.import_proto(
        config, input_filename=input_filename
    )
    if save_to_known:
        config.known_types.update(new_typedefs)
    else:
        return new_typedefs


NAME_REGEX = re.compile(r"\A[a-zA-Z][a-zA-Z0-9_]*\Z")


def validate_typedef(typedef, old_typedef=None, config=None, _path=None):
    """Attempt to validate a type definition object is valid.

    This function attempts to ensure a type definition is valid before it is
    used to encode/decode a message. This will make sure the field names are
    valid and field names/numbers are consistent. It is intended to be called
    after a user has edited the type definition to ensure the edits are valid.

    Args:
        typedef: The type definition object to validate. This should be a
            python dict derived from the dict returned  by a decode function.
        old_typedef: Optionally provide a old version of the type definition to
            compare the new type definnition to. If provided, this function
            will ensure any type changes are valid. For example, a field with a
            varint type can be changed to other varint types, but not a string
            or float.
        config: Optionally provide a config object which contains the
            `known_types` map to map message type names to known type definitions.
            Defaults to `blackboxprotobuf.lib.config.default`.
    Raises:
        TypedefException: Raises a TypedefException if the provided type
            definition is not valid.
    """
    if _path is None:
        _path = []
    if config is None:
        config = blackboxprotobuf.lib.config.default

    int_keys = set()
    field_names = set()
    for field_number, field_typedef in typedef.items():
        alt_field_number = None
        if "-" in str(field_number):
            field_number, alt_field_number = field_number.split("-")

        # Validate field_number is a number
        if not str(field_number).isdigit():
            raise TypedefException("Field number must be a digit: %s" % field_number)
        field_number = str(field_number)

        field_path = _path[:]
        field_path.append(field_number)

        # Check for duplicate field numbers
        if field_number in int_keys:
            raise TypedefException(
                "Duplicate field number: %s" % field_number, field_path
            )
        int_keys.add(field_number)

        # Must have a type field
        if "type" not in field_typedef:
            raise TypedefException(
                "Field number must have a type value: %s" % field_number, field_path
            )
        if alt_field_number is not None:
            if field_typedef["type"] != "message":
                raise TypedefException(
                    "Alt field number (%s) specified for non-message field: %s"
                    % (alt_field_number, field_number),
                    field_path,
                )

        valid_type_fields = [
            "type",
            "name",
            "field_order",
            "message_typedef",
            "message_type_name",
            "alt_typedefs",
            "example_value_ignored",
            "seen_repeated",
        ]
        for key, value in field_typedef.items():
            # Check field keys against valid values
            if key not in valid_type_fields:
                raise TypedefException(
                    'Invalid field key "%s" for field number %s' % (key, field_number),
                    field_path,
                )
            if (
                key in ["message_typedef", "message_type_name"]
                and not field_typedef["type"] == "message"
            ):
                raise TypedefException(
                    'Invalid field key "%s" for field number %s' % (key, field_number),
                    field_path,
                )
            if key == "group_typedef" and not field_typedef["type"] == "group":
                raise TypedefException(
                    'Invalid field key "%s" for field number %s' % (key, field_number),
                    field_path,
                )

            # Validate type value
            if key == "type":
                if value not in blackboxprotobuf.lib.types.type_maps.WIRETYPES:
                    raise TypedefException(
                        'Invalid type "%s" for field number %s' % (value, field_number),
                        field_path,
                    )
            # Check for duplicate names
            if key == "name" and value.strip() != "":
                if value.lower() in field_names:
                    raise TypedefException(
                        ('Duplicate field name "%s" for field ' "number %s")
                        % (value, field_number),
                        field_path,
                    )
                if not NAME_REGEX.match(value):
                    raise TypedefException(
                        (
                            'Invalid field name "%s" for field '
                            "number %s. Should match %s"
                        )
                        % (value, field_number, "[a-zA-Z_][a-zA-Z0-9_]*"),
                        field_path,
                    )
                if value != "":
                    field_names.add(value.lower())

            # Check if message type name is known
            if key == "message_type_name":
                if value not in config.known_types:
                    raise TypedefException(
                        (
                            'Message type "%s" for field number'
                            " %s is not known. Known types: %s"
                        )
                        % (value, field_number, config.known_types.keys()),
                        field_path,
                    )

            # Recursively validate inner typedefs
            if key in ["message_typedef", "group_typedef"]:
                if isinstance(value, dict):
                    if old_typedef is None:
                        validate_typedef(value, _path=field_path, config=config)
                    else:
                        validate_typedef(
                            value, old_typedef[field_number][key], _path=field_path
                        )
            if key == "alt_typedefs":
                for alt_field_number, alt_typedef in value.items():
                    if isinstance(alt_typedef, dict):
                        validate_typedef(alt_typedef, _path=field_path, config=config)

    if old_typedef is not None:
        wiretype_map = {}
        for field_number, value in old_typedef.items():
            wiretype_map[
                int(field_number)
            ] = blackboxprotobuf.lib.types.type_maps.WIRETYPES[value["type"]]
        for field_number, value in typedef.items():
            field_path = _path[:]
            field_path.append(str(field_number))
            if int(field_number) in wiretype_map:
                old_wiretype = wiretype_map[int(field_number)]
                if (
                    old_wiretype
                    != blackboxprotobuf.lib.types.type_maps.WIRETYPES[value["type"]]
                ):
                    raise TypedefException(
                        (
                            "Wiretype for field number %s does"
                            " not match old type definition"
                        )
                        % field_number,
                        field_path,
                    )


def _json_safe_transform(values, typedef, toBytes, config=None):
    # Python's JSON doesn't have a default way to handle 'bytes' types. To
    # handle this, we want some string like encoding which JSON can handle but
    # can also handle arbitrary bytes. This method get's more complicated than
    # just converting all bytes since on re-encoding we need to know which ones
    # were transformed and which are supposed to actually be strings

    # A built-for binary encoding method like hex or base64 would be 'proper',
    # but doesn't really give any information to a reader. In some cases, a
    # binary blob may have embedded strings or integer values that would be
    # beneficial to quickly skim.

    # This uses latin1 encoding because it can handle arbitrary bytes, prints
    # ASCII characters and can be decoded back to the same exact byte string.
    # It's possible I missed another encoding method that matches these
    # properties across python2.7 and python3.9, but had issues with some other
    # backslash escape mechanisms parsing back to bytes.

    if config is None:
        config = blackboxprotobuf.lib.config.default
    name_map = {
        item["name"]: number
        for number, item in typedef.items()
        if ("name" in item and item["name"] != "")
    }
    if not isinstance(values, dict):
        # this function should only ever be called on a message, error out if
        # it is not one. This usually means a type got swapped around
        raise EncoderException(
            "Error performing _json_safe_transform on message. Field was expected to be a message but was not: %r"
            % values
        )
    for name, value in values.items():
        alt_number = None
        base_name = name
        if "-" in name:
            base_name, alt_number = name.split("-")

        if base_name in name_map:
            field_number = name_map[base_name]
        else:
            field_number = base_name

        if field_number not in typedef or "type" not in typedef[field_number]:
            raise EncoderException("Field %r not found in typedef or does not have type attribute." % field_number)

        field_type = typedef[field_number]["type"]
        if field_type == "message":
            field_typedef = _get_typedef_for_message(typedef[field_number], config)
            if alt_number is not None:
                # if we have an alt type, then let's look that up instead
                if alt_number not in typedef[field_number].get("alt_typedefs", {}):
                    raise TypedefException(
                        (
                            "Provided alt field name/number "
                            "%s is not valid for field_number %s"
                        )
                        % (alt_number, field_number)
                    )
                field_type = typedef[field_number]["alt_typedefs"][alt_number]
                if isinstance(field_type, dict):
                    field_typedef = field_type
                    field_type = "message"

        is_list = isinstance(value, list)
        field_values = value if is_list else [value]
        for i, field_value in enumerate(field_values):
            if field_type == "bytes":
                if toBytes:
                    field_values[i] = field_value.encode("latin1")
                else:
                    field_values[i] = field_value.decode("latin1")
            elif field_type == "message":
                field_values[i] = _json_safe_transform(
                    field_value,
                    field_typedef,
                    toBytes,
                    config=config,
                )

        # convert back to single value if needed
        if not is_list:
            values[name] = field_values[0]
        else:
            values[name] = field_values
    return values


def _get_typedef_for_message(field_typedef, config):
    assert field_typedef["type"] == "message"
    if "message_typedef" in field_typedef:
        return field_typedef["message_typedef"]
    elif field_typedef.get("message_type_name"):
        if field_typedef["message_type_name"] not in config.known_types:
            raise TypedefException(
                "Got 'message_type_name' not in known_messages: %s"
                % field_typedef["message_type_name"]
            )
        return config.known_types[field_typedef["message_type_name"]]
    else:
        raise TypedefException(
            "Got 'message' type without typedef or type name: %s" % field_typedef
        )


def _sort_output(value, typedef, config=None):
    # Sort output by the field number in the typedef. Helps with readability in
    # a JSON dump
    output_dict = collections.OrderedDict()
    if config is None:
        config = blackboxprotobuf.lib.config.default

    # Make a list of all the field names we have, aggregate together the alt fields as well
    field_names = {}
    for field_name in value.keys():
        if "-" in field_name:
            field_name_base, alt_number = field_name.split("-")
        else:
            field_name_base = field_name
            alt_number = None
        field_names.setdefault(field_name_base, []).append((field_name, alt_number))

    for field_number, field_def in sorted(typedef.items(), key=lambda t: int(t[0])):
        field_number = str(field_number)
        seen_field_names = field_names.get(field_number, [])

        # Try getting matching fields by name as well
        if field_def.get("name", "") != "":
            field_name = field_def["name"]
            seen_field_names.extend(field_names.get(field_name, []))

        for field_name, alt_number in seen_field_names:
            field_type = field_def["type"]
            field_message_typedef = None
            if field_type == "message":
                field_message_typedef = _get_typedef_for_message(field_def, config)

            if alt_number is not None:
                if alt_number not in field_def["alt_typedefs"]:
                    raise TypedefException(
                        (
                            "Provided alt field name/number "
                            "%s is not valid for field_number %s"
                        )
                        % (alt_number, field_number)
                    )
                field_type = field_def["alt_typedefs"][alt_number]
                if isinstance(field_type, dict):
                    field_message_typedef = field_type
                    field_type = "message"

            if field_type == "message":
                if not isinstance(value[field_name], list):
                    output_dict[field_name] = _sort_output(
                        value[field_name], field_message_typedef
                    )
                else:
                    output_dict[field_name] = []
                    for field_value in value[field_name]:
                        output_dict[field_name].append(
                            _sort_output(field_value, field_message_typedef)
                        )
            else:
                output_dict[field_name] = value[field_name]

    return output_dict


def sort_typedef(typedef):
    """Apply special sorting rules to the type definition to improve readability.

    Sorts the fields of a type definition so that important fields such as the
    'type' or 'name' are at the top and don't get buried beneath longer fields
    like 'message_typedef'. This will also sort the keys of the
    'message_typedef' based on the field number.
    Args:
        typedef - dictionary representing a Blackboxprotobuf type definition
    Returns:
        A new OrderedDict object containing the contents of the typedef
        argument sorted for readability.
    """

    # Sort output by field number and sub_keys so name then type is first

    TYPEDEF_KEY_ORDER = [
        "name",
        "type",
        "message_type_name",
        "example_value_ignored",
        "field_order",
    ]
    output_dict = collections.OrderedDict()

    for field_number, field_def in sorted(typedef.items(), key=lambda t: int(t[0])):
        output_field_def = collections.OrderedDict()
        field_def = field_def.copy()
        for key in TYPEDEF_KEY_ORDER:
            if key in field_def:
                output_field_def[key] = field_def[key]
                del field_def[key]
        for key, value in field_def.items():

            if key == "message_typedef":
                output_field_def[key] = sort_typedef(value)
            else:
                output_field_def[key] = value
        output_dict[field_number] = output_field_def
    return output_dict


def _annotate_typedef(typedef, message):
    # Add values from message into the typedef so it's easier to figure out
    # which field when you're editing manually

    for field_number, field_def in typedef.items():
        field_value = None
        field_name = str(field_number)
        if field_name not in message and field_def.get("name", "") != "":
            field_name = field_def["name"]

        if field_name in message:
            field_value = message[field_name]

            if field_def["type"] == "message":
                if isinstance(field_value, list):
                    for value in field_value:
                        _annotate_typedef(field_def["message_typedef"], value)
                else:
                    _annotate_typedef(field_def["message_typedef"], field_value)
            else:
                field_def["example_value_ignored"] = field_value

        # Add a blank name field if the field doesn't have one, so it's easier
        # to add
        if 'name' not in field_def:
            field_def['name'] = ""

def _strip_typedef_annotations(typedef):
    # Remove example values placed by _annotate_typedef
    for _, field_def in typedef.items():
        if "example_value_ignored" in field_def:
            del field_def["example_value_ignored"]
        if "message_typedef" in field_def:
            _strip_typedef_annotations(field_def["message_typedef"])
