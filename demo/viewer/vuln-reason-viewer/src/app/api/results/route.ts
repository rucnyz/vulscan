// app/api/results/route.ts
import { NextResponse } from 'next/server';
import { ResultData } from '@/lib/types';
import fs from 'fs';
import path from 'path';

export async function GET(request: Request) {
  try {
    // Get the filename from the query parameter
    const { searchParams } = new URL(request.url);
    const filename = searchParams.get('file') || 'results.json'; // Default to results.json if not specified
    
    // Ensure the filename is sanitized to prevent directory traversal attacks
    const sanitizedFilename = path.basename(filename);
    
    // Only allow .json files
    if (!sanitizedFilename.endsWith('.json')) {
      return NextResponse.json({ error: 'Invalid file format' }, { status: 400 });
    }
    
    const filePath = path.join(process.cwd(), 'data', sanitizedFilename);
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ error: 'File not found' }, { status: 404 });
    }
    
    const fileContents = fs.readFileSync(filePath, 'utf8');
    const data: ResultData = JSON.parse(fileContents);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error loading results:', error);
    return NextResponse.json({ error: 'Failed to load results data' }, { status: 500 });
  }
}