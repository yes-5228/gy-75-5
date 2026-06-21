<script setup>
import { computed, reactive, ref } from 'vue'
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

const formErrors = reactive({
  inspector: '',
  checklist: '',
  elevatorId: '',
})

const currentHandlingPlan = computed(() => props.handlingPlans[form.result] || '')

function validateForm() {
  let valid = true
  formErrors.inspector = ''
  formErrors.checklist = ''
  formErrors.elevatorId = ''

  if (!form.inspector.trim()) {
    formErrors.inspector = '请填写巡检员姓名'
    valid = false
  }
  if (!form.checklist.trim()) {
    formErrors.checklist = '请填写检查项内容'
    valid = false
  }
  if (!form.elevatorId) {
    formErrors.elevatorId = '请选择电梯'
    valid = false
  }
  return valid
}

function clearFieldError(field) {
  if (formErrors[field]) {
    formErrors[field] = ''
  }
}

function submit() {
  if (props.submitting) return
  if (!validateForm()) return
  emit('create', { ...form, elevatorId: Number(form.elevatorId) })
}

function closeWarning() {
  emit('close-severe-dialog')
}

function handleGoToFaults() {
  emit('go-to-faults')
}

function resetForm() {
  Object.assign(form, { inspector: '', result: 'Normal', checklist: '', attachmentUrl: '', elevatorId: '' })
  formErrors.inspector = ''
  formErrors.checklist = ''
  formErrors.elevatorId = ''
}

defineExpose({ resetForm })
</script>

<template>
  <div class="view-stack">
    <section class="panel">
      <SectionHeader title="Upload Inspection Record" description="Register result, checklist, and attachment URL" />
      <div v-if="submitError" class="notice error">{{ submitError }}</div>
      <form class="form-grid" @submit.prevent="submit">
        <label :class="{ 'input-error': formErrors.inspector }">
          <span>Inspector <em class="required-mark">*</em></span>
          <input v-model="form.inspector" placeholder="Inspector name" :disabled="submitting" @input="clearFieldError('inspector')" />
          <span v-if="formErrors.inspector" class="field-error">{{ formErrors.inspector }}</span>
        </label>
        <label>
          <span>Result</span>
          <select v-model="form.result" :disabled="submitting">
            <option value="Normal">Normal</option>
            <option value="Slight Abnormal">Slight Abnormal</option>
            <option value="Severe Abnormal">Severe Abnormal</option>
          </select>
        </label>
        <label :class="{ 'input-error': formErrors.elevatorId }">
          <span>Elevator <em class="required-mark">*</em></span>
          <select v-model="form.elevatorId" :disabled="submitting" @change="clearFieldError('elevatorId')">
            <option value="" disabled>Select elevator</option>
            <option v-for="elevator in elevators" :key="elevator.id" :value="elevator.id">
              {{ elevator.code }} - {{ elevator.building }} {{ elevator.unit }}
            </option>
          </select>
          <span v-if="formErrors.elevatorId" class="field-error">{{ formErrors.elevatorId }}</span>
        </label>
        <label>
          <span>Attachment URL</span>
          <input v-model="form.attachmentUrl" placeholder="Image or document URL" :disabled="submitting" />
        </label>
        <label class="wide" :class="{ 'input-error': formErrors.checklist }">
          <span>Checklist <em class="required-mark">*</em></span>
          <textarea v-model="form.checklist" rows="3" placeholder="Door, cabin, machine room, traction system, and safety checks" :disabled="submitting" @input="clearFieldError('checklist')"></textarea>
          <span v-if="formErrors.checklist" class="field-error">{{ formErrors.checklist }}</span>
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
              <span class="fault-info-label">Fault Type</span>
              <span class="fault-info-value">{{ severeFaultInfo.faultType }}</span>
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
          <div class="fault-description-card">
            <p class="fault-description-label">Problem Description</p>
            <p class="fault-description-text">{{ severeFaultInfo.description }}</p>
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
