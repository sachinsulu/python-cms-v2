from django.db import models

from apps.core.models import BaseContentModel


class Package(BaseContentModel):
    ROOM     = "room"
    NON_ROOM = "non_room"
    TYPE_CHOICES = [(ROOM, "Room"), (NON_ROOM, "Non-Room")]

    description = models.TextField(blank=True)
    image = models.ForeignKey(
        "media.MediaAsset",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="packages",
    )
    package_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=NON_ROOM
    )

    @property
    def is_room(self):
        return self.package_type == self.ROOM

    class Meta(BaseContentModel.Meta):
        verbose_name_plural = "Packages"


class SubPackage(BaseContentModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name="sub_packages"
    )
    description = models.TextField(blank=True)
    image = models.ForeignKey(
        "media.MediaAsset",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_packages_media",
    )
    price     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    capacity  = models.PositiveIntegerField(null=True, blank=True)
    beds      = models.PositiveIntegerField(null=True, blank=True)
    amenities = models.JSONField(
        default=list, blank=True, help_text="List of amenity strings"
    )

    class Meta(BaseContentModel.Meta):
        verbose_name_plural = "Sub-Packages"

        # Composite index — speeds up the query pattern used by every
        # sub-package list view and API endpoint:
        #   SELECT ... WHERE package_id = ? ORDER BY position
        indexes = [
            models.Index(
                fields=["package", "position"],
                name="subpkg_pkg_pos_idx",
            ),
        ]

        # DB-level uniqueness guarantee for (package, position).
        # The Python-layer _assign_position() scoping (Phase 3.3) prevents
        # duplicates under normal ORM usage. This constraint is the final
        # safety net for anything that bypasses the ORM: direct DB writes,
        # data migrations, management commands, or shell inserts.
        constraints = [
            models.UniqueConstraint(
                fields=["package", "position"],
                name="uniq_subpkg_pos_per_pkg",
            ),
        ]

    def save(self, *args, **kwargs):
        """
        Override save() to scope position assignment to the parent Package.

        Problem:
            BaseContentModel._assign_position() uses the global MAX(position)
            across the entire SubPackage table. Sub-packages in different
            packages therefore share one counter:

                Package A sub-packages → positions 1, 2, 3
                Package B sub-packages → positions 4, 5        ← wrong

            Ordering within each package becomes non-contiguous and the
            drag-sort UI displays an incorrect initial order.

        Fix:
            For new instances (pk is None), pre-call _assign_position() with
            a queryset scoped to sub-packages of the same parent Package.
            This sets self.position to the correct per-parent value:

                Package A sub-packages → positions 1, 2, 3
                Package B sub-packages → positions 1, 2        ← correct

            When BaseContentModel.save() then calls _assign_position() inside
            its own transaction block, the "position > 0" guard in
            SortableMixin sees that self.position is already set and returns
            immediately — the scoped value is preserved.

        Edits (self.pk is not None) are completely unaffected:
            _assign_position() is a no-op for existing instances regardless
            of scope.
        """
        if not self.pk:
            # Scope the position counter to this package's children only.
            # The row-level lock inside _assign_position() serialises
            # concurrent creates within the same package, preventing
            # duplicate positions even under high concurrency.
            scope = SubPackage.objects.filter(package=self.package)
            self._assign_position(scope_qs=scope)

        # Delegate slug generation, GlobalSlug upsert, and the actual DB
        # write to BaseContentModel.save(). The position > 0 guard ensures
        # _assign_position() inside super() is a no-op for new instances
        # where we have already computed and stored the scoped position.
        super().save(*args, **kwargs)