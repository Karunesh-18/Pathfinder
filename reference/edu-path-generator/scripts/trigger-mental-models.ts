/**
 * Script to manually trigger mental model image generation for a learning path
 *
 * Usage (in browser console on your app):
 * 1. Find a learning path ID from your app
 * 2. Run: triggerMentalModels('your-path-id-here', 'Topic Name')
 */

import { createClient } from '@supabase/supabase-js';

// You'll need to replace these with your actual values
const SUPABASE_URL = process.env.VITE_SUPABASE_URL || 'https://your-project-ref.supabase.co';
const SUPABASE_ANON_KEY = process.env.VITE_SUPABASE_ANON_KEY || 'your-anon-key-here';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

export async function triggerMentalModels(pathId: string, topic: string) {
  console.log(`🎨 Triggering mental model generation for path: ${pathId}`);
  console.log(`📚 Topic: ${topic}`);

  try {
    // First, fetch the learning steps for this path
    const { data: steps, error: stepsError } = await supabase
      .from('learning_steps')
      .select('title, description')
      .eq('learning_path_id', pathId)
      .order('order_index');

    if (stepsError) {
      console.error('❌ Error fetching steps:', stepsError);
      return;
    }

    if (!steps || steps.length === 0) {
      console.error('❌ No steps found for this path');
      return;
    }

    console.log(`✅ Found ${steps.length} steps`);

    // Create path summary
    const pathSummary = `A comprehensive ${steps.length}-step learning journey about "${topic}"`;

    // Call the edge function
    const { data, error } = await supabase.functions.invoke('generate-path-mental-models', {
      body: {
        pathId,
        topic,
        pathSummary,
        stepCount: steps.length
      }
    });

    if (error) {
      console.error('❌ Error invoking function:', error);
      return;
    }

    console.log('✅ Successfully triggered mental model generation!');
    console.log('📊 Response:', data);
    console.log('⏳ Images will be generated in the background. Check the Images mode in your app.');

    return data;
  } catch (error) {
    console.error('❌ Unexpected error:', error);
  }
}

// Example usage in browser console:
// triggerMentalModels('your-path-id', 'React Hooks')
