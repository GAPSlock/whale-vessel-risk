# NOAA/NEFSC NARWSS Data Request Specification

## Request Context
**Target Dataset**: North Atlantic Right Whale Sighting Survey (NARWSS) 
**Temporal Scope**: 2017–2021
**Spatial Scope**: Gulf of Maine / Cape Cod Bay (Approx. 41.0–43.5°N, -71.5–-68.5°W)
**Purpose**: Parameterizing a continuous-time predictive collision risk model. We require the continuous **event/effort trackline geometry** and associated environmental flight logs, not merely the aggregate occurrence/sighting exports, to construct a rigorous sparse-observation likelihood model.

---

## 1. Survey Effort / Event Data (Track Geometry)

To construct the observation model and distinguish surveyed absence from unobserved states, the continuous flight track data and environmental conditions are required.

### Mandatory Fields
*   **Timestamp/Date**: High-resolution local or UTC datetime of the event/track vertex.
*   **Latitude/Longitude**: High-resolution continuous trackline geometry (point vertices or line segments).
*   **Event Number**: Unique identifier for the logging event.
*   **Survey/Flight ID**: Identifier tying continuous effort to a specific flight/survey day.
*   **Platform/Aircraft**: Identifier for the observation platform.
*   **Flight Type / Leg Type**: E.g., transit, systematic survey, circling. (Critical for filtering off-effort vs. on-effort data).
*   **Visibility**: E.g., nautical miles or categorical.
*   **Beaufort State**: Sea state code (0-9).

### Optional (High-Value) Fields
*   **Altitude**: Aircraft altitude (critical for distance-sampling perception models).
*   **Speed**: Ground speed or indicated airspeed.
*   **Heading**: Direction of travel.
*   **Glare**: Glare severity/angle affecting observer availability.
*   **Other Observation Conditions**: Cloud cover, observer positions, or subjective quality scores.

---

## 2. Sightings Data

To link detected biological presence with the effort tracklines.

### Mandatory Fields
*   **Species**: Confirmed taxonomic identification (*Eubalaena glacialis*).
*   **Timestamp**: Exact time of the sighting, matching the effort track time scale.
*   **Latitude/Longitude**: Exact location of the detected animal(s).
*   **Group Size**: Number of individuals in the sighting cluster.
*   **Sighting Number / Event Linkage**: A relational key linking the biological sighting to the corresponding Survey Effort/Event log.

### Optional (High-Value) Fields
*   **Perpendicular Distance / Declination Angle**: Critical for establishing the distance-decay detection function.
*   **Individual ID**: Catalog identification (if photographic matching was achieved).

---

## 3. Data Integration Note
The core requirement is that the **Sightings** data must be relationally linkable to the **Survey Effort** data, allowing us to reconstruct the exact environmental conditions (Beaufort, Visibility) and aircraft state (Altitude, Leg Type) at the moment of—or in the absence of—a sighting.
