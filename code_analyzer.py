#!/usr/bin/env python3
"""
Analizador de Código Sospechoso
Detecta patrones maliciosos en archivos ejecutables y scripts.
"""

import os
import re
import hashlib
import math
import configparser
import logging
from typing import Dict, List, Set, Optional, Tuple
from collections import Counter

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    print("Warning: python-magic no disponible. Análisis de tipo de archivo limitado.")

class CodeAnalyzer:
    """Analizador de código para detectar patrones maliciosos"""
    
    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.config = config
        self.logger = logger
        
        # Cache para análisis previos
        self.analysis_cache = {}
        self.use_cache = config.getboolean('performance', 'use_file_cache', fallback=True)
        self.cache_duration = config.getint('performance', 'cache_duration', fallback=3600)
        
        # Cargar patrones de configuración
        self._load_patterns()
        
        # Configurar magic si está disponible
        if MAGIC_AVAILABLE:
            try:
                self.magic = magic.Magic(mime=True)
            except:
                self.magic = None
                self.logger.warning("Error inicializando python-magic")
        else:
            self.magic = None
            
    def _load_patterns(self):
        """Carga patrones maliciosos desde la configuración"""
        # Patrones de código malicioso
        patterns_str = self.config.get('code_analysis', 'malicious_patterns', 
                                     fallback='CreateRemoteThread,VirtualAllocEx,WriteProcessMemory')
        self.malicious_patterns = [
            re.compile(pattern.strip(), re.IGNORECASE) 
            for pattern in patterns_str.split(',')
        ]
        
        # Strings sospechosos
        strings_str = self.config.get('code_analysis', 'suspicious_strings',
                                    fallback='password,admin,exploit')
        self.suspicious_strings = [s.strip().lower() for s in strings_str.split(',')]
        
        # Threshold de entropía
        self.entropy_threshold = self.config.getfloat('code_analysis', 'entropy_threshold', 
                                                     fallback=7.0)
        
        # Hashes maliciosos conocidos
        hashes_str = self.config.get('process_monitoring', 'malicious_hashes', fallback='')
        self.malicious_hashes = set(h.strip().lower() for h in hashes_str.split(',') if h.strip())
        
    def is_suspicious_file(self, file_path: str) -> bool:
        """Determina si un archivo es sospechoso"""
        try:
            # Verificar cache
            if self.use_cache and file_path in self.analysis_cache:
                cache_entry = self.analysis_cache[file_path]
                if self._is_cache_valid(cache_entry):
                    return cache_entry['is_suspicious']
            
            # Verificaciones básicas
            if not os.path.exists(file_path):
                return False
                
            file_size = os.path.getsize(file_path)
            max_size = self.config.getint('file_monitoring', 'max_file_size', fallback=52428800)
            
            if file_size > max_size:
                self.logger.info(f"Archivo demasiado grande para análisis: {file_path}")
                return False
                
            # Realizar análisis
            analysis_result = self._analyze_file(file_path)
            
            # Guardar en cache
            if self.use_cache:
                self.analysis_cache[file_path] = {
                    'is_suspicious': analysis_result['is_suspicious'],
                    'timestamp': analysis_result['timestamp'],
                    'reasons': analysis_result['reasons']
                }
            
            return analysis_result['is_suspicious']
            
        except Exception as e:
            self.logger.error(f"Error analizando archivo {file_path}: {e}")
            return False
            
    def _analyze_file(self, file_path: str) -> Dict:
        """Análisis completo de un archivo"""
        reasons = []
        is_suspicious = False
        
        try:
            # 1. Verificar hash MD5
            file_hash = self._calculate_md5(file_path)
            if file_hash in self.malicious_hashes:
                reasons.append(f"Hash MD5 malicioso conocido: {file_hash}")
                is_suspicious = True
                
            # 2. Análisis de contenido
            content_analysis = self._analyze_content(file_path)
            if content_analysis['suspicious']:
                reasons.extend(content_analysis['reasons'])
                is_suspicious = True
                
            # 3. Análisis de entropía
            entropy = self._calculate_entropy(file_path)
            if entropy > self.entropy_threshold:
                reasons.append(f"Alta entropía detectada: {entropy:.2f}")
                is_suspicious = True
                
            # 4. Análisis de tipo de archivo
            file_type_analysis = self._analyze_file_type(file_path)
            if file_type_analysis['suspicious']:
                reasons.extend(file_type_analysis['reasons'])
                is_suspicious = True
                
            # 5. Análisis de nombre de archivo
            name_analysis = self._analyze_filename(file_path)
            if name_analysis['suspicious']:
                reasons.extend(name_analysis['reasons'])
                is_suspicious = True
                
        except Exception as e:
            self.logger.error(f"Error en análisis detallado de {file_path}: {e}")
            
        return {
            'is_suspicious': is_suspicious,
            'reasons': reasons,
            'file_hash': file_hash if 'file_hash' in locals() else None,
            'entropy': entropy if 'entropy' in locals() else None,
            'timestamp': os.path.getmtime(file_path)
        }
        
    def _analyze_content(self, file_path: str) -> Dict:
        """Analiza el contenido del archivo buscando patrones maliciosos"""
        reasons = []
        suspicious = False
        
        try:
            # Leer archivo en chunks para archivos grandes
            chunk_size = 8192
            pattern_matches = Counter()
            string_matches = Counter()
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                        
                    # Convertir a string para análisis de texto
                    try:
                        text_chunk = chunk.decode('utf-8', errors='ignore').lower()
                    except:
                        text_chunk = str(chunk).lower()
                        
                    # Buscar patrones maliciosos
                    for pattern in self.malicious_patterns:
                        matches = pattern.findall(text_chunk)
                        if matches:
                            pattern_matches[pattern.pattern] += len(matches)
                            
                    # Buscar strings sospechosos
                    for sus_string in self.suspicious_strings:
                        if sus_string in text_chunk:
                            string_matches[sus_string] += text_chunk.count(sus_string)
            
            # Evaluar resultados
            if pattern_matches:
                reasons.append(f"Patrones maliciosos encontrados: {dict(pattern_matches)}")
                suspicious = True
                
            if string_matches:
                reasons.append(f"Strings sospechosos encontrados: {dict(string_matches)}")
                # Solo marcar como sospechoso si hay muchas coincidencias
                if sum(string_matches.values()) > 5:
                    suspicious = True
                    
        except Exception as e:
            self.logger.error(f"Error analizando contenido de {file_path}: {e}")
            
        return {'suspicious': suspicious, 'reasons': reasons}
        
    def _analyze_file_type(self, file_path: str) -> Dict:
        """Analiza el tipo de archivo y detecta inconsistencias"""
        reasons = []
        suspicious = False
        
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Verificar con magic si está disponible
            if self.magic:
                try:
                    mime_type = self.magic.from_file(file_path)
                    
                    # Detectar extensiones falsas
                    if file_ext == '.txt' and 'executable' in mime_type:
                        reasons.append("Archivo ejecutable con extensión .txt")
                        suspicious = True
                    elif file_ext == '.jpg' and 'executable' in mime_type:
                        reasons.append("Archivo ejecutable con extensión de imagen")
                        suspicious = True
                    elif file_ext == '.pdf' and 'executable' in mime_type:
                        reasons.append("Archivo ejecutable con extensión .pdf")
                        suspicious = True
                        
                except Exception as e:
                    self.logger.debug(f"Error con magic en {file_path}: {e}")
            
            # Verificar archivos ejecutables sin extensión
            if not file_ext:
                with open(file_path, 'rb') as f:
                    header = f.read(4)
                    if header.startswith(b'MZ'):  # PE executable
                        reasons.append("Ejecutable PE sin extensión")
                        suspicious = True
                        
        except Exception as e:
            self.logger.error(f"Error analizando tipo de archivo {file_path}: {e}")
            
        return {'suspicious': suspicious, 'reasons': reasons}
        
    def _analyze_filename(self, file_path: str) -> Dict:
        """Analiza el nombre del archivo por patrones sospechosos"""
        reasons = []
        suspicious = False
        
        try:
            filename = os.path.basename(file_path).lower()
            
            # Obtener patrones sospechosos de configuración
            patterns_str = self.config.get('file_monitoring', 'suspicious_patterns', 
                                         fallback='*malware*,*virus*,*trojan*')
            
            for pattern in patterns_str.split(','):
                pattern = pattern.strip().replace('*', '.*')
                if re.search(pattern, filename):
                    reasons.append(f"Nombre de archivo sospechoso: {filename}")
                    suspicious = True
                    break
                    
            # Verificar nombres de archivos comunes de malware
            malware_names = [
                'svchost.exe', 'winlogon.exe', 'explorer.exe', 'system.exe'
            ]
            
            # Si está en ubicación sospechosa con nombre legítimo
            suspicious_paths = ['temp', 'downloads', 'appdata']
            file_dir = file_path.lower()
            
            if filename in malware_names and any(path in file_dir for path in suspicious_paths):
                reasons.append(f"Archivo con nombre legítimo en ubicación sospechosa: {file_path}")
                suspicious = True
                
        except Exception as e:
            self.logger.error(f"Error analizando nombre de archivo {file_path}: {e}")
            
        return {'suspicious': suspicious, 'reasons': reasons}
        
    def _calculate_entropy(self, file_path: str) -> float:
        """Calcula la entropía de un archivo"""
        try:
            with open(file_path, 'rb') as f:
                # Leer muestra del archivo
                data = f.read(8192)
                
            if not data:
                return 0.0
                
            # Calcular frecuencias de bytes
            frequencies = Counter(data)
            data_len = len(data)
            
            # Calcular entropía
            entropy = 0.0
            for count in frequencies.values():
                probability = count / data_len
                entropy -= probability * math.log2(probability)
                
            return entropy
            
        except Exception as e:
            self.logger.error(f"Error calculando entropía de {file_path}: {e}")
            return 0.0
            
    def _calculate_md5(self, file_path: str) -> str:
        """Calcula el hash MD5 de un archivo"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest().lower()
        except Exception as e:
            self.logger.error(f"Error calculando MD5 de {file_path}: {e}")
            return ""
            
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Verifica si una entrada del cache es válida"""
        import time
        current_time = time.time()
        cache_time = cache_entry.get('timestamp', 0)
        return (current_time - cache_time) < self.cache_duration
        
    def get_analysis_report(self, file_path: str) -> Dict:
        """Obtiene un reporte completo del análisis de un archivo"""
        if not os.path.exists(file_path):
            return {'error': 'Archivo no encontrado'}
            
        try:
            analysis = self._analyze_file(file_path)
            
            report = {
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'is_suspicious': analysis['is_suspicious'],
                'reasons': analysis['reasons'],
                'file_hash': analysis.get('file_hash'),
                'entropy': analysis.get('entropy'),
                'last_modified': analysis.get('timestamp')
            }
            
            return report
            
        except Exception as e:
            return {'error': f'Error generando reporte: {e}'}
            
    def update_malicious_hashes(self, new_hashes: List[str]):
        """Actualiza la lista de hashes maliciosos"""
        self.malicious_hashes.update(h.lower() for h in new_hashes)
        self.logger.info(f"Agregados {len(new_hashes)} nuevos hashes maliciosos")
        
    def clear_cache(self):
        """Limpia el cache de análisis"""
        self.analysis_cache.clear()
        self.logger.info("Cache de análisis limpiado")

if __name__ == "__main__":
    import sys
    
    # Ejemplo de uso
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    logger = logging.getLogger('CodeAnalyzer')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(handler)
    
    analyzer = CodeAnalyzer(config, logger)
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        report = analyzer.get_analysis_report(file_path)
        print(f"Análisis de: {file_path}")
        print(f"Sospechoso: {'SÍ' if report.get('is_suspicious', False) else 'NO'}")
        if report.get('reasons'):
            print("Razones:")
            for reason in report['reasons']:
                print(f"  - {reason}")
    else:
        print("Uso: python code_analyzer.py <ruta_del_archivo>")