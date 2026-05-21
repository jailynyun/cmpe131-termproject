<script setup>
import { computed, onMounted, ref } from 'vue'
import { tenantConfig } from '../config/tenantConfig.js'
import { bookingService } from '../services/bookingService.js'
import { useAuth } from '../composables/useAuth.js'

const { userId, userEmail } = useAuth()

const isLoading = ref(true)
const errorMessage = ref('')
const trips = ref([])
const editingHotel = ref(null)
const editingActivity = ref(null)

const hotelEditForm = ref({
  Room_Request_Type: '',
  Special_Request: '',
})

const activityEditForm = ref({
  Time_Slot: '',
  Is_Private: false,
})

const roomRequestOptions = [
  'Honeymoon Decoration',
  'Ocean View',
  'King Bed',
  'Late Check-In',
  'Champagne Setup',
  'Private Pool Villa',
]

function formatDate(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value || 'N/A'
  return date.toLocaleDateString('en-GB', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const tripCountLabel = computed(() => {
  const tripCount = trips.value.length
  return tripCount === 1 ? '1 saved trip' : `${tripCount} saved trips`
})

async function loadTrips(showLoading = true) {
  if (showLoading) {
    isLoading.value = true
  }
  errorMessage.value = ''

  try {
    trips.value = await bookingService.listBookings({
      userId: userId.value,
      agentId: tenantConfig.agentId,
    })
  } catch (error) {
    errorMessage.value = error.message || 'Unable to load saved trips.'
    trips.value = []
  } finally {
    if (showLoading) {
      isLoading.value = false
    }
  }
}

function startHotelEdit(hotel) {
  editingHotel.value = hotel.Reservation_No

  hotelEditForm.value = {
    Room_Request_Type: hotel.Room_Request_Type || '',
    Special_Request: hotel.Special_Request || '',
  }
}

function startActivityEdit(activity) {
  editingActivity.value = activity.Activity_Reservation_Id

  activityEditForm.value = {
    Time_Slot: activity.Time_Slot || '',
    Is_Private: Boolean(activity.Is_Private),
  }
}

async function saveHotelEdit(trip, hotel) {
  const scrollY = window.scrollY

  await bookingService.updateHotelReservation(
    trip.bookingId,
    hotel.Reservation_No,
    {
      Room_Request_Type: hotelEditForm.value.Room_Request_Type,
      Special_Request: hotelEditForm.value.Special_Request,
    }
  )

  editingHotel.value = null
  await loadTrips(false)

  window.scrollTo({
    top: scrollY,
    behavior: 'instant',
  })
}

async function saveActivityEdit(trip, activity) {
  const scrollY = window.scrollY

  await bookingService.updateActivityReservation(
    trip.bookingId,
    activity.Activity_Reservation_Id,
    {
      Time_Slot: activityEditForm.value.Time_Slot,
      Is_Private: activityEditForm.value.Is_Private,
    }
  )

  editingActivity.value = null
  await loadTrips(false)

  window.scrollTo({
    top: scrollY,
    behavior: 'instant',
  })
}

onMounted(() => {
  loadTrips()
})
</script>

<template>
  <div class="my-trips-view">
    <div class="my-trips-view__hero">
      <div>
        <p class="my-trips-view__eyebrow">Agent {{ tenantConfig.agentId }}</p>
        <h1 class="my-trips-view__title">My Trips</h1>
        <p class="my-trips-view__sub">
          Saved trips for {{ userEmail || `User ${userId}` }} with {{ tenantConfig.brandName }}.
        </p>
      </div>
      <div class="my-trips-view__summary">{{ tripCountLabel }}</div>
    </div>

    <div v-if="isLoading" class="state-card">Loading saved trips...</div>
    <div v-else-if="errorMessage" class="state-card state-card--error">{{ errorMessage }}</div>
    <div v-else-if="trips.length === 0" class="state-card">No saved trips found for this user and agent.</div>

    <div v-else class="trips-list">
      <article v-for="trip in trips" :key="trip.bookingId" class="trip-card">
        <div class="trip-card__header">
          <div>
            <p class="trip-card__meta">Booking #{{ trip.bookingId }}</p>
            <h2 class="trip-card__title">{{ formatDate(trip.startDate) }} to {{ formatDate(trip.endDate) }}</h2>
          </div>

          <div class="trip-card__pill">
            {{ trip.flightReservations.length }} flights ·
            {{ trip.hotelReservations.length }} hotels ·
            {{ (trip.activityReservations || []).length }} activities
          </div>
        </div>

        <section class="trip-section">
          <h3 class="trip-section__title">Flight Details</h3>
          <p v-if="trip.flightReservations.length === 0" class="trip-section__empty">No flights saved for this trip.</p>
          <div v-else class="reservation-grid">
            <div v-for="flight in trip.flightReservations" :key="`${trip.bookingId}-${flight.Reservation_No}`" class="reservation-card">
              <div class="reservation-card__title">Flight Reservation</div>
              <div><strong>Airline code:</strong> {{ flight.Airline_Code || 'N/A' }}</div>
              <div><strong>Flight number:</strong> {{ flight.Flight_Number || 'N/A' }}</div>
              <div>{{ flight.Origin_Airport_Code }} to {{ flight.Destination_Airport_Code }}</div>
              <div>Departure: {{ formatDate(flight.Departure_Date) }} {{ flight.Departure_Time }}</div>
              <div>Arrival: {{ formatDate(flight.Arrive_Date) }} {{ flight.Arrive_Time }}</div>
              <div>Rate: ${{ Number(flight.Rate || 0).toLocaleString() }}</div>
            </div>
          </div>
        </section>

        <section class="trip-section">
          <h3 class="trip-section__title">Hotel Details</h3>
          <p v-if="trip.hotelReservations.length === 0" class="trip-section__empty">No hotel saved for this trip.</p>
          <div v-else class="reservation-grid">
            <div v-for="hotel in trip.hotelReservations" :key="`${trip.bookingId}-${hotel.Reservation_No}`" class="reservation-card">
              <div class="reservation-card__title">Hotel Reservation</div>
              <div><strong>Hotel Name:</strong> {{ hotel.Hotel_Name || 'Hotel name unavailable' }}</div>
              <div>Check in: {{ formatDate(hotel.Check_In_Date) }} {{ hotel.Check_In_Time }}</div>
              <div>Check out: {{ formatDate(hotel.Check_Out_Date) }} {{ hotel.Check_Out_Time }}</div>
              <div>Rate: ${{ Number(hotel.Rate || 0).toLocaleString() }}</div>
              <p v-if="hotel.Room_Request_Type">
                <strong>Room Request:</strong> {{ hotel.Room_Request_Type }}
              </p>
              <p v-if="hotel.Special_Request">
                <strong>Special Request:</strong> {{ hotel.Special_Request }}
              </p>
              <button
                type="button"
                @click="startHotelEdit(hotel)"
                class="edit-button"
              >
                Edit Hotel
              </button>
              <div
                v-if="editingHotel === hotel.Reservation_No"
                class="edit-form"
              >
                <label>
                  Room Request
                  <select
                    v-model="hotelEditForm.Room_Request_Type"
                    class="request-input"
                  >
                    <option value="">Select a room preference</option>

                    <option
                      v-for="option in roomRequestOptions"
                      :key="option"
                      :value="option"
                    >
                      {{ option }}
                    </option>
                  </select>
                </label>

                <label>
                  Special Request
                  <textarea
                    v-model="hotelEditForm.Special_Request"
                    maxlength="500"
                  ></textarea>
                </label>

                <button
                  type="button"
                  @click="saveHotelEdit(trip, hotel)"
                  class="save-button"
                >
                  Save Hotel Changes
                </button>
              </div>
            </div>
          </div>
        </section>

        <section class="trip-section">
          <h3 class="trip-section__title">Activity Details</h3>

          <p
            v-if="(trip.activityReservations || []).length === 0"
            class="trip-section__empty"
          >
            No activities saved for this trip.
          </p>

          <div v-else class="reservation-grid">
            <div
              v-for="activity in trip.activityReservations || []"
              :key="`${trip.bookingId}-${activity.Activity_Reservation_Id}`"
              class="reservation-card"
            >
              <div class="reservation-card__title">
                Activity Reservation
              </div>

              <div>
                <strong>Activity Name:</strong>
                {{ activity.Activity_Name || 'N/A' }}
              </div>

              <div v-if="activity.Location">
                <strong>Location:</strong>
                {{ activity.Location }}
              </div>

              <div>
                <strong>Date:</strong>
                {{ formatDate(activity.Activity_Date) }}
              </div>

              <div v-if="activity.Time_Slot">
                <strong>Time Slot:</strong>
                {{ activity.Time_Slot }}
              </div>

              <div>
                <strong>Private Activity:</strong>
                {{ activity.Is_Private ? 'Yes' : 'No' }}
              </div>

              <div v-if="activity.Price">
                <strong>Price:</strong>
                ${{ Number(activity.Price).toLocaleString() }}
              </div>
              <button
                type="button"
                @click="startActivityEdit(activity)"
                class="edit-button"
              >
                Edit Activity
              </button>

              <div
                v-if="editingActivity === activity.Activity_Reservation_Id"
                class="edit-form"
              >
                <label>
                  Time Slot
                  <input
                    v-model="activityEditForm.Time_Slot"
                    type="text"
                  />
                </label>

                <label class="checkbox-label">
                  <input
                    v-model="activityEditForm.Is_Private"
                    type="checkbox"
                  />
                  Private Activity
                </label>

                <button
                  type="button"
                  @click="saveActivityEdit(trip, activity)"
                  class="save-button"
                >
                  Save Activity Changes
                </button>
              </div>
            </div>
          </div>
        </section>
      </article>
    </div>
  </div>
</template>

<style scoped>
.my-trips-view {
  min-height: calc(100vh - 56px);
  background: var(--color-bg);
  padding: 2rem;
}

.edit-button,
.save-button {
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.edit-button {
  background: #e8eefc;
  color: #1a365d;
}

.save-button {
  background: #1a365d;
  color: white;
}

.edit-form {
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.edit-form input,
.edit-form textarea,
.edit-form select {
  width: 100%;
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--color-border);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.my-trips-view__hero {
  max-width: 1200px;
  margin: 0 auto 1.5rem;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
}

.my-trips-view__eyebrow {
  margin: 0 0 0.35rem;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-accent-dark);
}

.my-trips-view__title {
  margin: 0;
  font-size: 2rem;
  color: var(--color-primary-dark);
}

.my-trips-view__sub {
  margin: 0.5rem 0 0;
  color: var(--color-text-muted);
}

.my-trips-view__summary {
  padding: 0.6rem 0.9rem;
  border-radius: 999px;
  background: #fff;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  font-weight: 700;
}

.state-card {
  max-width: 1200px;
  margin: 0 auto;
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 2rem;
  color: var(--color-text-muted);
}

.state-card--error {
  color: #c0392b;
}

.trips-list {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.trip-card {
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: 18px;
  padding: 1.5rem;
  box-shadow: 0 10px 24px rgba(26, 54, 93, 0.06);
}

.trip-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.trip-card__meta {
  margin: 0 0 0.35rem;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.trip-card__title {
  margin: 0;
  color: var(--color-primary-dark);
  font-size: 1.2rem;
}

.trip-card__pill {
  padding: 0.45rem 0.75rem;
  border-radius: 999px;
  background: var(--color-primary-bg);
  color: var(--color-primary-dark);
  font-size: 0.85rem;
  font-weight: 700;
  white-space: nowrap;
}

.trip-section + .trip-section {
  margin-top: 1.25rem;
}

.trip-section__title {
  margin: 0 0 0.75rem;
  color: var(--color-text);
  font-size: 1rem;
}

.trip-section__empty {
  margin: 0;
  color: var(--color-text-muted);
}

.reservation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.75rem;
}

.reservation-card {
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 1rem;
  background: #fcfdff;
  color: var(--color-text);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.reservation-card__title {
  font-weight: 700;
  color: var(--color-primary-dark);
}

@media (max-width: 768px) {
  .my-trips-view {
    padding: 1rem;
  }

  .my-trips-view__hero,
  .trip-card__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>