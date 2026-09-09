<script setup>
import { ref, watch } from 'vue'
const props = defineProps({ modules: Array, selected: Array, user: Object })
const emit = defineEmits(['submit','logout'])
const chosen = ref([...props.selected])
watch(() => props.selected, value => { chosen.value = [...value] })
function toggle(id) { if (chosen.value.includes(id)) chosen.value = chosen.value.filter(item => item !== id); else if (chosen.value.length < 8) chosen.value.push(id) }
</script>
<template><section class="onboarding-page"><button class="onboarding-exit" @click="$emit('logout')">退出登录</button><div class="onboarding-inner"><div class="onboarding-kicker">STEP 1 · PERSONALIZE</div><h1>告诉我们你感兴趣的内容</h1><p>选择 3–8 个兴趣，我们会为你生成专属校园信息流。</p><div class="interest-grid"><button v-for="module in modules" :key="module.id" :class="{selected: chosen.includes(module.id)}" @click="toggle(module.id)"><span class="interest-icon">{{ module.icon || '✦' }}</span><span>{{ module.name }}</span><span v-if="chosen.includes(module.id)" class="selected-check">✓</span></button></div><div class="onboarding-footer"><span>已选择 <strong>{{ chosen.length }}</strong> / 8</span><button class="primary-button" :disabled="chosen.length < 3" @click="$emit('submit', chosen)">继续 <span>→</span></button></div></div></section></template>
