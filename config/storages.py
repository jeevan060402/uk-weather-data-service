from azure.storage.blob import ContentSettings
from django.core.files.base import File
from django.core.files.utils import validate_file_name  # type: ignore
from storages.backends.azure_storage import AzureStorage
from storages.utils import clean_name


class CustomAzureStorage(AzureStorage):
    def _save(self, name, content, **kwargs):
        cleaned_name = clean_name(name)
        name = self._get_valid_path(name)
        params = self._get_content_settings_parameters(name, content)

        overwrite = self.overwrite_files

        if kwargs.get("content_type"):
            params["content_type"] = kwargs["content_type"]
            kwargs.pop("content_type")

        if kwargs.get("overwrite"):
            overwrite = kwargs["overwrite"]
            kwargs.pop("overwrite")

        # Unwrap django file (wrapped by parent's save call)
        if isinstance(content, File):
            content = content.file

        content.seek(0)
        self.client.upload_blob(
            name,
            content,
            content_settings=ContentSettings(**params),
            max_concurrency=self.upload_max_conn,  # type: ignore
            timeout=self.timeout,  # type: ignore
            overwrite=overwrite,  # type: ignore
        )
        return cleaned_name

    def save(self, name, content, max_length=None, **kwargs):
        """
        Save new content to the file specified by name. The content should be
        a proper File object or any Python file-like object, ready to be read
        from the beginning.
        """
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name

        if not hasattr(content, "chunks"):
            content = File(content, name)

        # Ensure that the name is valid, before and after having the storage
        # system potentially modifying the name. This duplicates the check made
        # inside `get_available_name` but it's necessary for those cases where
        # `get_available_name` is overriden and validation is lost.
        validate_file_name(name, allow_relative_path=True)

        # Potentially find a different name depending on storage constraints.
        name = self.get_available_name(name, max_length=max_length)
        # Validate the (potentially) new name.
        validate_file_name(name, allow_relative_path=True)

        # The save operation should return the actual name of the file saved.
        name = self._save(name, content, **kwargs)
        # Ensure that the name returned from the storage system is still valid.
        validate_file_name(name, allow_relative_path=True)
        return name

    # These methods are part of the public API, with default implementations.
