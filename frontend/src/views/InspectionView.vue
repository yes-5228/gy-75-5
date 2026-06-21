<script setup>
import { computed, nextTick, reactive, ref } from 'vue'
import { AlertTriangle, ArrowRight, Upload } from 'lucide-vue-next'
import DataTable from '../components/DataTable.vue'
import SectionHeader from '../components/SectionHeader.vue'
import StatusBadge from '../components/StatusBadge.vue'

const props = defineProps({
  records: { type: Array, required: true },
  elevators: { type: Array, required: true },
  handlingPlans: { type: Object, default: () => ({}) },
  submitting: { type: Boolean, default: false },
  fieldErrors: { type: Object, default: () => ({}) },
  severeFaultInfo: { type: Object, default: null },
})

const emit = defineEmits(['create', 'close-severe-dialog', 'go-to-faults'])

const form = reactive({
  inspector: '',
  result: 'Normal',
  checklist: '',
  problemDescription: '',
  attachmentUrl: '',
  elevatorId: '',
})

const localErrors = reactive({
  inspector: '',
  checklist: '',
  elevatorId: '',
  problemDescription: '',
})

const inspectorRef = ref(null)
const elevatorRef = ref(null)
const checklistRef = ref(null)
const problemDescriptionRef = ref(null)

const isSevereAbnormal = computed(() => form.result === 'Severe Abnormal')
const currentHandlingPlan = computed(() => props.handlingPlans[form.result] || '')

function getDisplayError(field) {
  return localErrors[field] || props.fieldErrors[field] || ''
}

function clearFieldError(field) {
  if (localErrors[field]) {
    localErrors[field] = ''
  }
  emit('clear-field-error', field)
}

function validateForm() {
  let valid = true
  localErrors.inspector = ''
  localErrors.checklist = ''
  localErrors.elevatorId = ''
  localErrors.problemDescription = ''

  if (!form.inspector.trim()) {
    localErrors.inspector = '请填写巡检员姓名'
    valid = false
  }
  if (!form.elevatorId) {
    localErrors.elevatorId = '请选择电梯'
    valid = false
  }
  if (!form.checklist.trim()) {
    localErrors.checklist = '请填写检查项内容'
    valid = false
  }
  if (isSevereAbnormal.value && !form.problemDescription.trim()) {
    localErrors.problemDescription = '严重异常必须填写问题描述'
    valid = false
  }
  return valid
}

async function focusFirstError() {
  await nextTick()
  const order = [inspectorRef, elevatorRef, checklistRef, problemDescriptionRef]
  for (const inputRef of order) {
    if (inputRef.value) {
      const el = inputRef.value.$el || inputRef.value
      const input = el.querySelector?.('input, select, textarea') || el
      input.focus?.()
      input.scrollIntoView?.({ behavior: 'smooth', block: 'center' })
      break
    }
  }
}

function submit() {
  if (props.submitting) return
  if (!validateForm()) {
    focusFirstError()
    return
  }
  const payload = { ...form, elevatorId: Number(form.elevatorId) }
  if (!isSevereAbnormal.value) {
    delete payload.problemDescription
  }
  emit('create', payload)
}

function closeWarning() {
  emit('close-severe-dialog')
}

function handleGoToFaults() {
  emit('go-to-faults')
}

function resetForm() {
  Object.assign(form, { inspector: '', result: 'Normal', checklist: '', problemDescription: '', attachmentUrl: '', elevatorId: '' })
  localErrors.inspector = ''
  localErrors.checklist = ''
  localErrors.elevatorId = ''
  localErrors.problemDescription = ''
}

defineExpose({ resetForm, focusFirstError })
</script>

<template>
  <div class="view-stack">
    <section class="panel">
      <SectionHeader title="Upload Inspection Record" description="Register result, checklist, and attachment URL" />
      <form class="form-grid" @submit.prevent="submit">
        <label ref="inspectorRef" :class="{ 'input-error': getDisplayError('inspector') }">
          <span>Inspector <em class="required-mark">*</em></span>
          <input v-model="form.inspector" placeholder="Inspector name" :disabled="submitting" @input="clearFieldError('inspector')" />
          <span v-if="getDisplayError('inspector')" class="field-error">{{ getDisplayError('inspector') }}</span>
        </label>
        <label>
          <span>Result</span>
          <select v-model="form.result" :disabled="submitting">
            <option value="Normal">Normal</option>
            <option value="Slight Abnormal">Slight Abnormal</option>
            <option value="Severe Abnormal">Severe Abnormal</option>
          </select>
        </label>
        <label ref="elevatorRef" :class="{ 'input-error': getDisplayError('elevatorId') }">
          <span>Elevator <em class="required-mark">*</em></span>
          <select v-model="form.elevatorId" :disabled="submitting" @change="clearFieldError('elevatorId')">
            <option value="" disabled>Select elevator</option>
            <option v-for="elevator in elevators" :key="elevator.id" :value="elevator.id">
              {{ elevator.code }} - {{ elevator.building }} {{ elevator.unit }}
            </option>
          </select>
          <span v-if="getDisplayError('elevatorId')" class="field-error">{{ getDisplayError('elevatorId') }}</span>
        </label>
        <label>
          <span>Attachment URL</span>
          <input v-model="form.attachmentUrl" placeholder="Image or document URL" :disabled="submitting" />
        </label>
        <label ref="checklistRef" class="wide" :class="{ 'input-error': getDisplayError('checklist') }">
          <span>Checklist <em class="required-mark">*</em></span>
          <textarea v-model="form.checklist" rows="3" placeholder="List all checked items: door, cabin, machine room, traction system, safety devices..." :disabled="submitting" @input="clearFieldError('checklist')"></textarea>
          <span v-if="getDisplayError('checklist')" class="field-error">{{ getDisplayError('checklist') }}</span>
        </label>
        <label v-if="isSevereAbnormal" ref="problemDescriptionRef" class="wide" :class="{ 'input-error': getDisplayError('problemDescription') }">
          <span>Problem Description <em class="required-mark">*</em></span>
          <textarea v-model="form.problemDescription" rows="3" placeholder="Describe the specific severe issue found during this inspection, separate from the checklist above" :disabled="submitting" @input="clearFieldError('problemDescription')"></textarea>
          <span v-if="getDisplayError('problemDescription')" class="field-error">{{ getDisplayError('problemDescription') }}</span>
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
