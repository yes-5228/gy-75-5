<script setup>
import { computed, reactive, ref } from 'vue'
import { AlertTriangle, Upload } from 'lucide-vue-next'
import DataTable from '../components/DataTable.vue'
import SectionHeader from '../components/SectionHeader.vue'
import StatusBadge from '../components/StatusBadge.vue'

const props = defineProps({
  records: { type: Array, required: true },
  elevators: { type: Array, required: true },
  handlingPlans: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['create'])

const form = reactive({
  inspector: '',
  result: 'Normal',
  checklist: '',
  attachmentUrl: '',
  elevatorId: '',
})

const showSevereWarning = ref(false)
const createdFault = ref(null)

const currentHandlingPlan = computed(() => props.handlingPlans[form.result] || '')

function submit() {
  emit('create', { ...form, elevatorId: Number(form.elevatorId) })
  if (form.result === 'Severe Abnormal') {
    showSevereWarning.value = true
  }
  Object.assign(form, { inspector: '', result: 'Normal', checklist: '', attachmentUrl: '', elevatorId: '' })
}

function closeWarning() {
  showSevereWarning.value = false
  createdFault.value = null
}
</script>

<template>
  <div class="view-stack">
    <section class="panel">
      <SectionHeader title="Upload Inspection Record" description="Register result, checklist, and attachment URL" />
      <form class="form-grid" @submit.prevent="submit">
        <label>
          <span>Inspector</span>
          <input v-model="form.inspector" required placeholder="Inspector name" />
        </label>
        <label>
          <span>Result</span>
          <select v-model="form.result">
            <option value="Normal">Normal</option>
            <option value="Slight Abnormal">Slight Abnormal</option>
            <option value="Severe Abnormal">Severe Abnormal</option>
          </select>
        </label>
        <label>
          <span>Elevator</span>
          <select v-model="form.elevatorId" required>
            <option value="" disabled>Select elevator</option>
            <option v-for="elevator in elevators" :key="elevator.id" :value="elevator.id">
              {{ elevator.code }} - {{ elevator.building }} {{ elevator.unit }}
            </option>
          </select>
        </label>
        <label>
          <span>Attachment URL</span>
          <input v-model="form.attachmentUrl" placeholder="Image or document URL" />
        </label>
        <label class="wide">
          <span>Checklist</span>
          <textarea v-model="form.checklist" required rows="3" placeholder="Door, cabin, machine room, traction system, and safety checks"></textarea>
        </label>
        <div v-if="currentHandlingPlan" class="wide handling-plan-hint">
          <strong>Handling Plan:</strong> {{ currentHandlingPlan }}
        </div>
        <button class="primary-action" type="submit">
          <Upload :size="17" />
          <span>Submit Record</span>
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

    <div v-if="showSevereWarning" class="modal-overlay" @click="closeWarning">
      <div class="modal-content severe-warning" @click.stop>
        <div class="modal-header">
          <AlertTriangle :size="24" class="warning-icon" />
          <h3>Severe Abnormal Detected</h3>
        </div>
        <div class="modal-body">
          <p>A severe abnormality has been recorded. A fault ticket has been automatically created for urgent repair.</p>
          <p class="warning-note">Please follow up on the fault report page to track the repair progress.</p>
        </div>
        <div class="modal-footer">
          <button class="primary-action" @click="closeWarning">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>
