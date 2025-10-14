import re
from typing import List, Tuple

class MarkdownCleaner:
    def clean_markdown_text(self, markdown_text: str) -> str:
        """
        Fungsi untuk membersihkan teks markdown dengan aturan khusus:
        - Heading tetap di baris terpisah
        - Tabel tetap di baris terpisah (tanpa separator row)
        - Label:value di gabung dalam satu baris (dipisah koma)
        - List item dengan bullet points digabung dalam satu baris
        
        Args:
            markdown_text: String markdown yang ingin dibersihkan.

        Returns:
            String yang telah dibersihkan.
        """
        lines = markdown_text.split('\n')
        cleaned_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()

            # Skip baris kosong
            if not line:
                i += 1
                continue

            # Skip table separator (| --- | --- |)
            if re.match(r'^\s*\|\s*[-:]+\s*\|', line):
                i += 1
                continue

            # Heading - tambahkan langsung
            if line.startswith('#'):
                cleaned_lines.append(line)
                i += 1
                continue

            # Table row - tambahkan langsung
            if re.match(r'^\s*\|.*\|\s*$', line):
                cleaned_lines.append(line)
                i += 1
                continue

            # Cek apakah ini blok label:value
            if self._is_label_value_line(line):
                merged_text, next_i = self._merge_label_value_block(lines, i)
                if merged_text:
                    cleaned_lines.append(merged_text)
                i = next_i
                continue

            # Cek apakah ini list items (bullet points)
            if line.startswith('-') or line.startswith('•'):
                merged_list, next_i = self._merge_list_items(lines, i)
                cleaned_lines.append(merged_list)
                i = next_i
                continue

            # Default: gabungkan paragraf biasa
            paragraph, next_i = self._merge_paragraph(lines, i)
            cleaned_lines.append(paragraph)
            i = next_i

        # Post-processing: tambahkan line break sebelum heading (kecuali yang pertama)
        final_lines = []
        for j, cl in enumerate(cleaned_lines):
            if cl.startswith('#') and j > 0:
                final_lines.append('')
            final_lines.append(cl)

        return '\n'.join(final_lines).strip()

    def _is_label_value_line(self, line: str) -> bool:
        """Cek apakah baris merupakan label dengan colon"""
        # Harus ada colon dan tidak boleh heading atau table
        if ':' not in line:
            return False
        if line.startswith('#') or line.startswith('|'):
            return False
        
        # Pastikan format seperti "Label:" atau "Label: value"
        parts = line.split(':', 1)
        if len(parts) >= 1 and parts[0].strip():
            return True
        
        return False

    def _merge_label_value_block(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """
        Gabungkan blok label:value menjadi satu baris dengan separator koma.
        Returns: (merged_text, next_index)
        """
        merged_items = []
        i = start_idx
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Stop jika baris kosong
            if not line:
                i += 1
                # Jika sudah ada items dan ketemu baris kosong, stop
                if merged_items:
                    break
                continue
            
            # Stop jika ketemu heading atau table
            if line.startswith('#') or re.match(r'^\s*\|', line):
                break
            
            # Proses jika ada colon
            if ':' in line:
                parts = line.split(':', 1)
                label = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ''
                
                # Jika value kosong, cek baris berikutnya
                if not value:
                    # Look ahead untuk value di baris berikutnya
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        
                        # Skip baris kosong
                        if not next_line:
                            j += 1
                            continue
                        
                        # Jika ketemu heading, table, atau label baru, stop
                        if next_line.startswith('#') or re.match(r'^\s*\|', next_line) or ':' in next_line:
                            break
                        
                        # Ini adalah value untuk label sebelumnya
                        value = next_line
                        i = j  # Update index ke baris value
                        break
                
                # Tambahkan ke merged items
                if label:  # Pastikan label tidak kosong
                    merged_items.append(f"{label}: {value}")
                
                i += 1
            else:
                # Jika tidak ada colon dan sudah punya items, stop
                if merged_items:
                    break
                # Jika belum ada items, ini mungkin value tanpa label (skip)
                i += 1
        
        merged_text = ', '.join(merged_items) if merged_items else ''
        return merged_text, i

    def _merge_list_items(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """
        Gabungkan list items menjadi satu baris.
        Returns: (merged_text, next_index)
        """
        items = []
        i = start_idx
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Stop jika baris kosong
            if not line:
                i += 1
                if items:  # Jika sudah ada items, stop
                    break
                continue
            
            # Stop jika ketemu heading atau table
            if line.startswith('#') or re.match(r'^\s*\|', line):
                break
            
            # Process bullet point
            if line.startswith('-') or line.startswith('•'):
                # Remove bullet point
                item = re.sub(r'^[-•]\s*', '', line)
                items.append(item)
                i += 1
            else:
                # Jika bukan bullet point dan sudah ada items, stop
                if items:
                    break
                i += 1
        
        merged_text = '  '.join(items) if items else ''
        return merged_text, i

    def _merge_paragraph(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """
        Gabungkan paragraf biasa.
        Returns: (merged_text, next_index)
        """
        paragraph_parts = [lines[start_idx].strip()]
        i = start_idx + 1
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Stop jika baris kosong
            if not line:
                i += 1
                break
            
            # Stop jika ketemu heading, table, atau label:value
            if line.startswith('#') or re.match(r'^\s*\|', line) or self._is_label_value_line(line):
                break
            
            # Stop jika ketemu bullet point
            if line.startswith('-') or line.startswith('•'):
                break
            
            paragraph_parts.append(line)
            i += 1
        
        paragraph = ' '.join(paragraph_parts)
        return paragraph, i