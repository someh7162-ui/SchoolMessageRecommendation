<script setup>
defineProps({ title: String, description: String, actionLabel: String })
defineEmits(['action'])
</script>
<template><div class="empty-state"><div class="empty-icon">⌁</div><h3>{{ title }}</h3><p>{{ description }}</p><button v-if="actionLabel" @click="$emit('action')">{{ actionLabel }}</button></div></template>
