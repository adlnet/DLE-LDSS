'use strict';

import { Dialog, DialogTitle, Transition, TransitionChild } from '@headlessui/react';
import { DuplicateIcon, ShareIcon } from '@heroicons/react/outline';
import { Fragment, useState } from 'react';

// import { useAuth } from '@/contexts/AuthContext';
import { useCallback } from 'react';

// import { xAPISendStatement } from '@/utils/xapi/xAPISendStatement';


export default function ShareButton({ courseId, courseTitle, courseDescription, user = true }) {
  
  // TODO
  // I refactored to add user into the function as a prop. Change to user default = false and delete this when
  // no longer demoing - MB
  //const { user } = true; // useAuth();

  // handle the copy to clipboard action
  const handleCopy = () => {
    navigator.clipboard.writeText(`${window.origin}/course/${courseId}`);
  };

  const handleClick = useCallback(() => {
    if (!user) return;
    console.count('share button clicked');

    /*

    const context = {
      actor: {
        first_name: user?.user?.first_name || 'anonymous',
        last_name: user?.user?.last_name || 'user',
      },
      verb: {
        id: 'https://w3id.org/xapi/tla/verbs/socialized',
        display: 'socialized',
      },
      object: {
        definitionName: courseTitle,
        description: courseDescription,
        id: `${window.origin}/course/${courseId}`,
      },
      resultExtName: 'https://w3id.org/xapi/ecc/result/extensions/CourseId',
      resultExtValue: courseId,
    };
*/

    handleCopy();
    openModal();
    
    // xAPISendStatement(context);
  }, [courseId, courseTitle, courseDescription, user]);

  // modal states
  let [isOpen, setIsOpen] = useState(false);
  const closeModal = () => setIsOpen(false);
  const openModal = () => setIsOpen(true);
  
  let url = '';
  if (typeof window !== "undefined"){
    url = `${window.origin}/course/${courseId}`;
  }

  return (
    <>
    <button
      onClick={handleClick}
      className='flex items-center gap-2 min-w-max whitespace-nowrap p-2 text-center text-white hover:shadow-md rounded-sm bg-blue-400 hover:bg-blue-600  font-medium transform transition-all duration-75 ease-in-out focus:ring-2 ring-blue-400 outline-none'
    >
      <ShareIcon className='h-5 w-5' />
      Share
    </button>
    <Transition appear show={isOpen} as={Fragment}>
    <Dialog
      as='div'
      className='fixed inset-0 z-10 overflow-y-auto'
      onClose={closeModal}
    >
      <div className='min-h-screen text-center'>
        <TransitionChild
          as={Fragment}
          enter='ease-out duration-200'
          enterFrom='opacity-0'
          enterTo='opacity-100'
          leave='ease-in duration-100'
          leaveFrom='opacity-100'
          leaveTo='opacity-0'
        >
          
        <div
        aria-hidden="true"
        className="fixed inset-0 bg-black bg-opacity-30"
      />        
      </TransitionChild>

        {/* This element is to trick the browser into centering the modal contents. */}
        <span
          className='inline-block h-screen align-middle'
          aria-hidden='true'
        >
          &#8203;
        </span>
        <TransitionChild
          as={Fragment}
          enter='ease-out duration-200'
          enterFrom='opacity-0 scale-95'
          enterTo='opacity-100 scale-100'
          leave='ease-in duration-100'
          leaveFrom='opacity-100 scale-100'
          leaveTo='opacity-0 scale-95'
        >
          <div className='inline-block w-full max-w-md p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-2xl'>
            <DialogTitle
              as='h3'
              className='text-lg font-medium leading-6 text-gray-900'
            >
              Link Copied!
            </DialogTitle>
            <div className='mt-2 w-full py-2 px-0.5 rounded-md overflow-y-auto custom-scroll border bg-gray-50 space-y-1'>
              {url}
            </div>

            
            <div className='mt-4'>
            <button
                type='button'
                className='inline-flex justify-center pl-2 pr-4 py-2 text-sm font-medium text-blue-900 bg-blue-100 border border-transparent rounded-md hover:bg-blue-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500'
                onClick={handleCopy}
              >
                <DuplicateIcon className='h-4 w-4 mr-1' />
                Copy
              </button>

              <button
                type='button'
                className='inline-flex justify-end ml-60 px-4 py-2 text-sm font-medium text-blue-900 bg-blue-100 border border-transparent rounded-md hover:bg-blue-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500'
                onClick={closeModal}
              >
                Close
              </button>
            </div>
          </div>
        </TransitionChild>
      </div>
    </Dialog>
  </Transition>
  </>
  );
}
