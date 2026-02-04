/**
 * Represents a course from the AETC provider
 */

export interface AetcCourse {
    id: number;
    agency_organization: string;
    course_provider: string;
    course_name: string;
    course_description: string;
    course_material_format: string;
    system_uii: string;
    course_administered_location: string;
    delivery_mode: string;
    system_operation: string;
    comments: string;

    // Tag so we know which provider this came from

    provider: 'aetc';
  }
  
  /**
   * Represents a course from the JKO provider
   */

  export interface JkoCourse {
    id: number;
    learning_resource_identifier: string;
    instance: string;
    delivery_mode: string;
    learning_resource_name: string;
    learning_resource_description: string;
    duration: string;
    catalog_url: string;

    provider: 'jko';
  }
  
  /**
   * A union of all provider-specific course schemas
   */

  export type Course = AetcCourse | JkoCourse;
  