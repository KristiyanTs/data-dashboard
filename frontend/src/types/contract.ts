export enum ContractCategory {
  GOODS = "goods",
  SERVICES = "services",
  WORKS = "works"
}

export interface Contract {
  id: number;
  company_name: string;
  contract_value: number;
  contract_date: string;
  category: ContractCategory;
  description?: string;
  created_at: string;
}

export interface ContractCreate {
  company_name: string;
  contract_value: number;
  contract_date: string;
  category: ContractCategory;
  description?: string;
}

export interface ContractList {
  contracts: Contract[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface Statistics {
  total_contracts: number;
  total_value: number;
  average_value: number;
  by_category: {
    [key: string]: {
      count: number;
      total_value: number;
    };
  };
}
