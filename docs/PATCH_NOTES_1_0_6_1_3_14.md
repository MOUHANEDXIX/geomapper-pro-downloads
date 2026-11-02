# GeoMapper Pro: Stable 1.0.6 and Beta 1.3.14

This update completes the P3 raster performance work and the Microsoft Store distribution assessment. It retains the coordinate, project/recovery, import, raster-control, vector, account and update safeguards documented in the [previous cumulative patch notes](https://github.com/MOUHANEDXIX/geomapper-pro-downloads/blob/main/docs/PATCH_NOTES_1_0_5_1_3_13.md).

Stable excludes the experimental AI assistant. Beta includes the same core changes plus the assistant and local Ollama workflow. Ordinary input height/Z and the existing numerical model remain unchanged. This patch adds no vertical datum/geoid conversion or independent OTC accuracy certification; geocentric Cartesian Z remains a coordinate component.

## Raster previews and source pixels

- Raster preview loading and image-format exports run in background jobs with progress, keeping the interface responsive.
- Display previews have a maximum edge of 2,048 pixels. Source dimensions and GCP coordinates stay in the original image's pixel space, including clicks, marker placement and saved projects.
- Reduced previews are used only for display. Exports reopen the original source and retain full resolution.
- Cached previews preserve palette transparency, grayscale alpha, CMYK colors and monochrome white pixels. Qt display images are created on the interface thread.
- TIFF exports from GCP georeferencing read the source through GDAL, preserving supported nodata, masks, band descriptions, units, scales, offsets and other band metadata. Selecting an ordinary target CRS replaces an obsolete STT marker instead of mislabelling the new file on reload.

## Cancellation and session protection

- Loading previews, exporting referenced rasters and exporting GCP-georeferenced images support cooperative cancellation. A cancelled load retains the previous image and controls.
- Workers use private raster engines and captured export inputs. Changes to GCPs invalidate the old fit and cancel an in-progress export before publication.
- Cancellation is checked after existing destination files are backed up and before the first destination replacement. Existing images and sidecars remain intact when cancellation is observed there.
- Once publication starts, it completes or rolls back as a protected operation. Cancellation cannot undo an export that has already committed.
- Native GDAL/Pillow calls finish at safe boundaries. They are not forcibly interrupted. Some codecs still decode a full native image even though the retained display buffer is bounded.
- Results and progress from an expired session are discarded. Signing out, or signing out and back in while a file chooser is open, cannot launch work from the earlier session.

## Distribution and existing service safeguards

The [Microsoft Store assessment](./MICROSOFT_STORE_ASSESSMENT.md) is complete. No Store package has been submitted or certified. A future MSIX pilot needs the actual reserved publisher/app identity, packaging tools and package acceptance tests. The versioned Windows installer remains the distribution route for this release; the updater's Ed25519 signature is separate from Windows publisher signing.

The P1/P2 service work remains in place: public deployment monitoring, backend readiness checks and a tested optional PostgreSQL rate-limit store. The shared store is an option for multiple backend instances; it does not imply that production was scaled or switched from its current single-instance configuration.

## Notes françaises

- Le chargement des aperçus raster et les exports image fonctionnent en arrière-plan avec progression. Le grand côté de l'aperçu est limité à 2 048 pixels ; les dimensions d'origine et les coordonnées pixel des points d'appui restent inchangées.
- L'aperçu réduit sert uniquement à l'affichage. Les exports utilisent les pixels sources en pleine résolution et conservent les valeurs nodata, masques et métadonnées de bandes pris en charge.
- La transparence des palettes, l'alpha des niveaux de gris, les couleurs CMJN et les pixels blancs monochromes restent visibles dans les aperçus.
- Une annulation observée avant le remplacement des destinations préserve les images et fichiers annexes existants. Une publication commencée se termine ou revient en arrière ; un export déjà terminé n'est pas effacé par une annulation tardive.
- Les appels natifs GDAL/Pillow atteignent une limite sûre avant de s'arrêter. Certains codecs décodent encore une image native complète, même si le tampon d'affichage conservé est borné.
- Les anciens retours de session sont ignorés. Une déconnexion pendant le choix d'un fichier ne lance pas de traitement depuis la session expirée.
- L'évaluation Microsoft Store est terminée, sans soumission ni certification Store. Stable reste sans assistant IA expérimental ; Beta conserve l'assistant et Ollama local.
- Le Z ordinaire et le modèle numérique existant restent inchangés. Aucune conversion verticale ni certification de précision OTC indépendante n'est ajoutée.
