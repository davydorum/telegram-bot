from django.db import models


class BaseModel(models.Model):
    """
    Abstract model with the core functionality used by the other three models
    to store the corresponding frames
    """

    chat_id = models.PositiveIntegerField("Chat Id")
    frame = models.PositiveIntegerField("Frame")
    created_at = models.DateTimeField("Created At", auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class Pending(BaseModel):
    """
    Stores the frames whent haven't been already evaluated by user.
    """

    pass


class Lower(BaseModel):
    """
    Stores the lower limit frames selected by user.
    """

    pass


class Upper(BaseModel):
    """
    Stores the upper limit frames selected by user.
    """

    pass
