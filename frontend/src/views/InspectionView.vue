<script setup>
import { computed, reactive } from 'vue'
import { AlertTriangle, ArrowRight, Upload } from 'lucide-vue-next'
import DataTable from '../components/DataTable.vue'
import SectionHeader from '../components/SectionHeader.vue'
import StatusBadge from '../components/StatusBadge.vue'

const props = defineProps({
  records: { type: Array, required: true },
  elevators: { type: Array, required: true },
  handlingPlans: { type: Object, default: () => ({}) },
  submitting: { type: Boolean, default: false },
  submitError: { type: String, default: '' },
  severeFaultInfo: { type: Object, default: null },
})

const emit = defineEmits(['create', 'close-severe-dialog', 'go-to-faults'])

const form = reactive({
  inspector: '',
  result: 'Normal',
  checklist: '',
  attachmentUrl: '',
  elevatorId: '',
})

const currentHandlingPlan = computed(() => props.handlingPlans[form.result] || '')

function submit() {
  if (props.submitting) return
  emit('create', { ...form, elevatorId: Number(form.elevatorId) })
}

function onSubmitSuccess() {
  Object.assign(form, { inspector: '', result: 'Normal', checklist: '', attachmentUrl: '', elevatorId: '' })
}

function closeWarning() {
  emit('close-severe-dialog')
}

function handleGoToFaults() {
  emit('go-to-faults')
}

function resetForm() {
  Object.assign(form, { inspector: '', result: 'Normal', checklist: '', attachmentUrl: '', elevatorId: '' })
}

defineExpose({ resetForm })
</script>

<template>
  <div class="view-stack">
    <section class="panel">
      <SectionHeader title="Upload Inspection Record" description="Register result, checklist, and attachment URL" />
      <div v-if="submitError" class="notice error">{{ submitError }}</div>
      <form class="form-grid" @submit.prevent="submit">
        <label>
          <span>Inspector</span>
          <input v-model="form.inspector" required placeholder="Inspector name" :disabled="submitting" />
        </label>
        <label>
          <span>Result</span>
          <select v-model="form.result" :disabled="submitting">
            <option value="Normal">Normal</option>
            <option value="Slight Abnormal">Slight Abnormal</option>
            <option value="Severe Abnormal">Severe Abnormal</option>
          </select>
        </label>
        <label>
          <span>Elevator</span>
          <select v-model="form.elevatorId" required :disabled="submitting">
            <option value="" disabled>Select elevator</option>
            <option v-for="elevator in elevators" :key="elevator.id" :value="elevator.id">
              {{ elevator.code }} - {{ elevator.building }} {{ elevator.unit }}
            </option>
          </select>
        </label>
        <label>
          <span>Attachment URL</span>
          <input v-model="form.attachmentUrl" placeholder="Image or document URL" :disabled="submitting" />
        </label>
        <label class="wide">
          <span>Checklist</span>
          <textarea v-model="form.checklist" required rows="3" placeholder="Door, cabin, machine room, traction system, and safety checks" :disabled="submitting"></textarea>
        </label>
        <div v-if="currentHandlingPlan" class="wide handling-plan-hint">
          <strong>Handling Plan:</strong> {{ currentHandlingPlan }}
        </div>
        <button class="primary-action" type="submit" :disabled="submitting">
          <Upload :size="17" :class="{ 'spin': submitting }" />
          <span>{{ submitting ? 'Submitting...' : 'Submit Record' }}</span>
        </button>
      </form>
    </section>

    <section class="panel">
      <SectionHeader title="Inspection Ledger" description="Newest records first" />
      <DataTable
        :columns="[
          { key: 'inspectedAt', label: 'Time' },
          { key: 'elevatorCode', label: 'Elevator' },
          { key: 'inspector', label: 'Inspector' },
          { key: 'result', label: 'Result' },
          { key: 'handlingPlan', label: 'Handling Plan' },
          { key: 'checklist', label: 'Checklist' },
          { key: 'attachmentUrl', label: 'Attachment' },
        ]"
        :rows="records"
      >
        <template #result="{ row }">
          <StatusBadge :value="row.result" />
        </template>
        <template #handlingPlan="{ row }">
          <span class="handling-plan-text">{{ row.handlingPlan }}</span>
        </template>
        <template #attachmentUrl="{ row }">
          <a v-if="row.attachmentUrl" :href="row.attachmentUrl" target="_blank" rel="noreferrer">Open</a>
          <span v-else>-</span>
        </template>
      </DataTable>
    </section>

    <div v-if="severeFaultInfo" class="modal-overlay" @click="closeWarning">
      <div class="modal-content severe-warning" @click.stop>
        <div class="modal-header">
          <AlertTriangle :size="24" class="warning-icon" />
          <h3>Severe Abnormal Detected</h3>
        </div>
        <div class="modal-body">
          <p>A severe abnormality has been recorded. A fault ticket has been automatically created for urgent repair.</p>
          <div class="fault-info-card">
            <div class="fault-info-row">
              <span class="fault-info-label">Fault Ticket No.</span>
              <span class="fault-info-value">#{{ severeFaultInfo.id }}</span>
            </div>
            <div class="fault-info-row">
              <span class="fault-info-label">Elevator</span>
              <span class="fault-info-value">{{ severeFaultInfo.elevatorCode }}</span>
            </div>
            <div class="fault-info-row">
              <span class="fault-info-label">Priority</span>
              <StatusBadge :value="severeFaultInfo.priority" />
            </div>
            <div class="fault-info-row">
              <span class="fault-info-label">Status</span>
              <StatusBadge :value="severeFaultInfo.status" />
            </div>
          </div>
          <p class="warning-note">Click the button below to view and track this fault report.</p>
        </div>
        <div class="modal-footer">
          <button class="secondary-action" @click="closeWarning">Close</button>
          <button class="primary-action" @click="handleGoToFaults">
            <span>Go to Fault Reports</span>
            <ArrowRight :size="16" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
