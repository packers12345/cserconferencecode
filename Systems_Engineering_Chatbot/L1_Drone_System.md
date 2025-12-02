# L1 System Model: Drone Delivery System

## 1. System Definition (L1 - Abstract/Functional)

At the L1 level, the drone delivery system is modeled as a transformation function that processes a **delivery request** and produces a **delivery confirmation**. We are not concerned with the physical drone, its motors, or the GPS unit (that's L2). We are only concerned with the abstract, functional behavior.

## 2. System Inputs and Outputs

*   **Input (u):** `DeliveryRequest`
    *   `payload_ID`: A unique identifier for the package.
    *   `pickup_location`: Coordinates for package pickup.
    *   `dropoff_location`: Coordinates for package drop-off.
    *   `max_delivery_time`: The maximum allowable time for the delivery.

*   **Output (y):** `DeliveryConfirmation`
    *   `payload_ID`: The same identifier for the package.
    *   `status`: A confirmation status (e.g., `SUCCESS`, `FAILURE`).
    *   `actual_delivery_time`: The time taken to complete the delivery.
    *   `proof_of_delivery`: A data object confirming delivery (e.g., a timestamp and photo hash).

## 3. Governing Function (Transformation)

The system `S_drone` can be described by the function `F_drone`:

`y = F_drone(u)`

Where `F_drone` represents the entire process of executing the delivery. The mathematical structure of this function can be modeled as a state-transition system or a queuing model, focusing on key performance parameters.

### Mathematical Representation (Simplified)

Let's model the `actual_delivery_time` as a function of the distance and average speed, including some overhead.

`distance = calculate_distance(pickup_location, dropoff_location)`
`flight_time = distance / average_drone_speed`
`overhead_time = pickup_time + dropoff_time`
`actual_delivery_time = flight_time + overhead_time`

The `status` is determined by a simple constraint:

`status = IF (actual_delivery_time <= max_delivery_time) THEN SUCCESS ELSE FAILURE`

This L1 model captures the *what* of the system (transforming a request to a confirmation) without detailing the *how* (the physical drone's flight dynamics).