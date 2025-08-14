import os
import logging
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)

class LegalKnowledgeBase:
    """Manages legal reference documents and knowledge base"""
    
    def __init__(self, data_dir: str = "legal_data"):
        self.data_dir = data_dir
        self.documents = []
        self.document_index = {}
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_legal_documents(self):
        """Load all legal documents from the data directory"""
        try:
            logger.info("Loading legal knowledge base documents...")
            
            # Define legal documents to load
            legal_files = [
                {
                    "filename": "indian_constitution.txt",
                    "title": "Constitution of India",
                    "category": "constitutional_law",
                    "source": "Government of India"
                },
                {
                    "filename": "indian_penal_code.txt",
                    "title": "Indian Penal Code, 1860",
                    "category": "criminal_law",
                    "source": "Legislative Department"
                },
                {
                    "filename": "crpc_sections.txt",
                    "title": "Code of Criminal Procedure, 1973",
                    "category": "procedural_law",
                    "source": "Legislative Department"
                },
                {
                    "filename": "civil_procedure_code.txt",
                    "title": "Code of Civil Procedure, 1908",
                    "category": "civil_law",
                    "source": "Legislative Department"
                },
                {
                    "filename": "evidence_act.txt",
                    "title": "Indian Evidence Act, 1872",
                    "category": "evidence_law",
                    "source": "Legislative Department"
                },
                {
                    "filename": "contract_act.txt",
                    "title": "Indian Contract Act, 1872",
                    "category": "contract_law",
                    "source": "Legislative Department"
                }
            ]
            
            loaded_count = 0
            
            for file_info in legal_files:
                file_path = os.path.join(self.data_dir, file_info["filename"])
                
                if os.path.exists(file_path):
                    content = self._load_text_file(file_path)
                    if content:
                        document = {
                            "id": f"legal_{file_info['filename'].replace('.txt', '')}",
                            "title": file_info["title"],
                            "content": content,
                            "category": file_info["category"],
                            "source": file_info["source"],
                            "filename": file_info["filename"]
                        }
                        
                        self.documents.append(document)
                        self.document_index[document["id"]] = document
                        loaded_count += 1
                        
                        logger.info(f"Loaded: {file_info['title']}")
                else:
                    # Create sample content if file doesn't exist
                    self._create_sample_legal_document(file_path, file_info)
                    logger.warning(f"Created sample file: {file_info['filename']}")
            
            # Load any additional text files in the directory
            self._load_additional_files()
            
            logger.info(f"Legal knowledge base loaded with {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to load legal documents: {str(e)}")
            raise
    
    def _load_text_file(self, file_path: str) -> str:
        """Load content from a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Basic content validation
            if len(content) < 100:  # Minimum content length
                logger.warning(f"File {file_path} has very little content")
                return None
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {str(e)}")
            return None
    
    def _create_sample_legal_document(self, file_path: str, file_info: Dict):
        """Create sample legal document content"""
        sample_content = self._get_sample_content(file_info["filename"])
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(sample_content)
        except Exception as e:
            logger.error(f"Failed to create sample file {file_path}: {str(e)}")
    
    def _get_sample_content(self, filename: str) -> str:
        """Generate sample content for legal documents"""
        samples = {
            "indian_constitution.txt": """CONSTITUTION OF INDIA

PREAMBLE
WE, THE PEOPLE OF INDIA, having solemnly resolved to constitute India into a SOVEREIGN SOCIALIST SECULAR DEMOCRATIC REPUBLIC and to secure to all its citizens:

JUSTICE, social, economic and political;
LIBERTY of thought, expression, belief, faith and worship;
EQUALITY of status and of opportunity;
and to promote among them all
FRATERNITY assuring the dignity of the individual and the unity and integrity of the Nation;

IN OUR CONSTITUENT ASSEMBLY this twenty-sixth day of November, 1949, do HEREBY ADOPT, ENACT AND GIVE TO OURSELVES THIS CONSTITUTION.

PART I - THE UNION AND ITS TERRITORY
Article 1. Name and territory of the Union
(1) India, that is Bharat, shall be a Union of States.
(2) The States and the territories thereof shall be as specified in the First Schedule.

Article 2. Admission or establishment of new States
Parliament may by law admit into the Union, or establish, new States on such terms and conditions as it thinks fit.

PART III - FUNDAMENTAL RIGHTS
Article 14. Equality before law
The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.

Article 19. Protection of certain rights regarding freedom of speech, etc.
(1) All citizens shall have the right—
(a) to freedom of speech and expression;
(b) to assemble peaceably and without arms;
(c) to form associations or unions;

Article 21. Protection of life and personal liberty
No person shall be deprived of his life or personal liberty except according to procedure established by law.""",

            "indian_penal_code.txt": """THE INDIAN PENAL CODE, 1860

CHAPTER I - INTRODUCTION
Section 1. Title and extent of operation of the Code
This Act shall be called the Indian Penal Code, and shall take effect throughout India.

Section 2. Punishment of offences committed within India
Every person shall be liable to punishment under this Code and not otherwise for every act or omission contrary to the provisions thereof, of which he shall be guilty within India.

CHAPTER II - GENERAL EXPLANATIONS
Section 6. Definitions in the Code to be understood subject to exceptions
Throughout this Code every definition of an offence, every penal provision, and every illustration of every such definition or penal provision, shall be understood subject to the general exceptions in Chapter IV.

CHAPTER XVI - OF OFFENCES AFFECTING THE HUMAN BODY
Section 299. Culpable homicide
Whoever causes death by doing an act with the intention of causing death, or with the intention of causing such bodily injury as is likely to cause death, or with the knowledge that he is likely by such act to cause death, commits the offence of culpable homicide.

Section 300. Murder
Except in the cases hereinafter excepted, culpable homicide is murder, if the act by which the death is caused is done with the intention of causing death.""",

            "crpc_sections.txt": """THE CODE OF CRIMINAL PROCEDURE, 1973

CHAPTER I - PRELIMINARY
Section 1. Short title, extent and commencement
(1) This Act may be called the Code of Criminal Procedure, 1973.
(2) It extends to the whole of India except the State of Jammu and Kashmir.

Section 2. Definitions
In this Code, unless the context otherwise requires,—
(a) "bailable offence" means an offence which is shown as bailable in the First Schedule;
(b) "cognizable offence" means an offence for which, and "cognizable case" means a case in which, a police officer may, in accordance with the First Schedule or under any other law for the time being in force, arrest without warrant;

CHAPTER V - ARREST OF PERSONS
Section 41. When police may arrest without warrant
Any police officer may without an order from a Magistrate and without a warrant, arrest any person—
(a) who has been concerned in any cognizable offence, or against whom a reasonable complaint has been made, or credible information has been received, or a reasonable suspicion exists, of his having been so concerned;

Section 50. Person arrested to be informed of grounds of arrest
Every police officer or other person arresting any person without warrant shall forthwith communicate to him the grounds on which such arrest is made.""",

            "civil_procedure_code.txt": """THE CODE OF CIVIL PROCEDURE, 1908

ORDER I - PARTIES TO SUITS
Rule 1. Who may be joined as plaintiffs
All persons may be joined in one suit as plaintiffs in whom any right to relief in respect of, or arising out of, the same act or transaction or series of acts or transactions is alleged to exist, whether jointly, severally or in the alternative.

Rule 10. Suit in name of wrong plaintiff
(1) Where a suit has been instituted in the name of the wrong person as plaintiff, or where it is doubtful whether it has been instituted in the name of the right plaintiff, the Court may at any stage of the proceedings allow the right person to be substituted or added as plaintiff upon such terms as the Court thinks just.

ORDER VI - PLEADINGS GENERALLY
Rule 2. Pleadings to state material facts
Every pleading shall contain, and contain only, a statement in a concise form of the material facts on which the party pleading relies for his claim or defence, as the case may be, but not the evidence by which they are to be proved.""",

            "evidence_act.txt": """THE INDIAN EVIDENCE ACT, 1872

CHAPTER I - PRELIMINARY
Section 1. Short title, extent and commencement
This Act may be called the Indian Evidence Act, 1872. It extends to the whole of India except the State of Jammu and Kashmir and applies to all judicial proceedings in or before any Court, including Courts-martial, other than Courts-martial convened under the Army Act, the Naval Discipline Act or the Air Force Act.

Section 3. Interpretation clause
In this Act the following words and expressions are used in the following senses, unless a contrary intention appears from the context:—
"Court" includes all Judges and Magistrates, and all persons, except arbitrators, legally authorised to take evidence.

CHAPTER II - ON RELEVANCY OF FACTS
Section 5. Evidence may be given of facts in issue and relevant facts
Evidence may be given in any suit or proceeding of the existence or non-existence of every fact in issue and of such other facts as are hereinafter declared to be relevant, and of no others.""",

            "contract_act.txt": """THE INDIAN CONTRACT ACT, 1872

CHAPTER I - PRELIMINARY
Section 1. Short title
This Act may be called the Indian Contract Act, 1872.

Section 2. Interpretation clause
In this Act the following words and expressions are used in the following senses, unless a contrary intention appears from the context:—
(a) When one person signifies to another his willingness to do or to abstain from doing anything, with a view to obtaining the assent of that other to such act or abstinence, he is said to make a proposal.
(b) When the person to whom the proposal is made signifies his assent thereto, the proposal is said to be accepted.

Section 10. What agreements are contracts
All agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object, and are not hereby expressly declared to be void."""
        }
        
        return samples.get(filename, f"Sample content for {filename}\n\nThis is a placeholder legal document.")
    
    def _load_additional_files(self):
        """Load any additional text files from the data directory"""
        try:
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.txt') and filename not in [doc['filename'] for doc in self.documents]:
                    file_path = os.path.join(self.data_dir, filename)
                    content = self._load_text_file(file_path)
                    
                    if content:
                        document = {
                            "id": f"additional_{filename.replace('.txt', '')}",
                            "title": filename.replace('_', ' ').replace('.txt', '').title(),
                            "content": content,
                            "category": "additional",
                            "source": "Local File",
                            "filename": filename
                        }
                        
                        self.documents.append(document)
                        self.document_index[document["id"]] = document
                        
        except Exception as e:
            logger.error(f"Failed to load additional files: {str(e)}")
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all loaded documents"""
        return self.documents
    
    def get_document_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Get a specific document by ID"""
        return self.document_index.get(doc_id)
    
    def search_documents(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Search documents by content or title"""
        results = []
        query_lower = query.lower()
        
        for doc in self.documents:
            if category and doc["category"] != category:
                continue
            
            # Search in title and content
            if (query_lower in doc["title"].lower() or 
                query_lower in doc["content"].lower()):
                results.append(doc)
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get all available document categories"""
        categories = set()
        for doc in self.documents:
            categories.add(doc["category"])
        return sorted(list(categories))
    
    def get_document_count(self) -> Dict[str, int]:
        """Get count of documents by category"""
        counts = {}
        for doc in self.documents:
            category = doc["category"]
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def export_knowledge_base(self, output_file: str):
        """Export knowledge base to JSON file"""
        try:
            export_data = {
                "documents": self.documents,
                "metadata": {
                    "total_documents": len(self.documents),
                    "categories": self.get_categories(),
                    "document_counts": self.get_document_count()
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Knowledge base exported to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export knowledge base: {str(e)}")
            raise